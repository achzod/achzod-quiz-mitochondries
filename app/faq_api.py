"""Parcours FAQ isolé ; aucune écriture dans les tables des autres applications."""
import copy
import hashlib
import hmac
import os
import random
import secrets
import time
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, StrictBool, StrictInt, Field, ConfigDict, TypeAdapter
from sqlalchemy import (create_engine, MetaData, Table, Column, String, Text,
                        Float, Boolean, JSON, Integer, select, func, UniqueConstraint)
from app.faq_content import QUESTIONS, VERSION

metadata = MetaData()
sessions = Table('faq_sessions', metadata,
    Column('token_hash', String(64), primary_key=True),
    Column('email', String(320), nullable=False),
    Column('newsletter', Boolean, nullable=False),
    Column('consent_version', String(40), nullable=False),
    Column('newsletter_confirmed', Boolean, nullable=False, default=False),
    Column('confirmation_hash', String(64), unique=True),
    Column('started_at', Float, nullable=False),
    Column('completed_at', Float),
    Column('ip_hash', String(64), nullable=False),
    Column('snapshot', JSON, nullable=False),
    Column('answers', JSON), Column('result', JSON),
    Column('is_qa', Boolean, nullable=False, default=False))

outbox = Table('faq_outbox', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('token_hash', String(64), nullable=False),
    Column('kind', String(20), nullable=False),
    Column('payload', JSON, nullable=False),
    Column('status', String(20), nullable=False, default='pending'),
    Column('attempts', Integer, nullable=False, default=0),
    Column('next_at', Float, nullable=False),
    Column('lease_at', Float), Column('provider_id', String(160)),
    Column('last_error', String(80)),
    UniqueConstraint('token_hash', 'kind', name='faq_unique_delivery'))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class PrivateJSONResponse(JSONResponse):
    def __init__(self, *args, **kwargs):
        headers = dict(kwargs.pop('headers', {}) or {})
        headers.update({'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
                        'X-Content-Type-Options': 'nosniff'})
        super().__init__(*args, headers=headers, **kwargs)


class Start(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr
    newsletter: StrictBool = False
    website: str = Field(default='', max_length=200)


class Submit(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str = Field(min_length=40, max_length=100)
    answers: Dict[str, StrictInt]


def public_result(conn, row):
    result = copy.deepcopy(row['result'])
    statuses = {j['kind']: j['status'] for j in conn.execute(
        select(outbox.c.kind, outbox.c.status).where(outbox.c.token_hash == row['token_hash'])).mappings()}
    result['email_status'] = statuses.get('results', 'pending')
    result['newsletter_status'] = ('excluded_qa' if row['is_qa'] else
        'not_requested' if not row['newsletter'] else
        statuses.get('newsletter', 'pending') if row['newsletter_confirmed'] else 'confirmation_required')
    return result


class Store:
    def __init__(self, database_url):
        if database_url.startswith('postgres://'):
            database_url = 'postgresql://' + database_url[len('postgres://'):]
        self.engine = create_engine(database_url, pool_pre_ping=True,
            connect_args={'check_same_thread': False, 'timeout': 30} if database_url.startswith('sqlite') else {})
        if database_url.startswith('sqlite'):
            from sqlalchemy import event
            @event.listens_for(self.engine, 'connect')
            def sqlite_config(connection, record):
                connection.execute('PRAGMA journal_mode=WAL')
                connection.execute('PRAGMA synchronous=FULL')
        metadata.create_all(self.engine)


class FAQRouter(APIRouter):
    store: Store
    provider: Any
    public_url: str
    admin_token: str
    secret: str
    min_duration: int
    notify_email: str


def build_router(database_url=None, provider=None, public_url=None, admin_token=None,
                 secret=None, min_duration=15, notify_email=None):
    url = database_url or os.environ.get('FAQ_DATABASE_URL')
    if not url:
        if os.environ.get('RENDER'):
            raise RuntimeError('FAQ_DATABASE_URL_REQUIRED')
        url = 'sqlite:///faq-local.sqlite'
    store = Store(url)
    router = FAQRouter(default_response_class=PrivateJSONResponse)
    router.store = store
    router.provider = provider
    router.public_url = public_url or os.environ.get('FAQ_PUBLIC_URL', 'http://127.0.0.1:8124')
    router.admin_token = admin_token or os.environ.get('FAQ_ADMIN_TOKEN', '')
    router.secret = secret or os.environ.get('FAQ_SECRET', 'development-only')
    router.min_duration = min_duration
    recipient = notify_email if notify_email is not None else os.environ.get('FAQ_NOTIFY_EMAIL', '')
    router.notify_email = str(TypeAdapter(EmailStr).validate_python(recipient)) if recipient else ''

    @router.get('/faq', include_in_schema=False)
    def page():
        return FileResponse(Path(__file__).resolve().parent.parent / 'templates' / 'faq.html',
            headers={'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
                     'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY'})

    @router.post('/api/faq/start')
    def start(data: Start, request: Request):
        if data.website:
            raise HTTPException(400, 'Formulaire non valide.')
        now = time.time()
        ip = request.client.host if request.client else 'unknown'
        ip_hash = hmac.new(router.secret.encode(), ip.encode(), hashlib.sha256).hexdigest()
        email = str(data.email)
        qa = bool(router.admin_token and hmac.compare_digest(request.headers.get('x-faq-admin', ''), router.admin_token))
        with store.engine.begin() as conn:
            ip_count = conn.execute(select(func.count()).select_from(sessions).where(
                sessions.c.ip_hash == ip_hash, sessions.c.started_at > now - 3600)).scalar_one()
            mail_count = conn.execute(select(func.count()).select_from(sessions).where(
                func.lower(sessions.c.email) == email.lower(), sessions.c.started_at > now - 86400)).scalar_one()
            if not qa and (ip_count >= 15 or mail_count >= 3):
                raise HTTPException(429, 'Trop de participations rapprochées. Réessaie plus tard.')
            token = secrets.token_urlsafe(36)
            snapshot = copy.deepcopy(QUESTIONS)
            for question in snapshot:
                order = list(range(4))
                random.SystemRandom().shuffle(order)
                question['correct'] = order.index(question['correct'])
                question['options'] = [question['options'][i] for i in order]
            conn.execute(sessions.insert().values(token_hash=digest(token), email=email,
                newsletter=data.newsletter, newsletter_confirmed=False,
                consent_version='faq-consent-v1', started_at=now, ip_hash=ip_hash,
                snapshot=snapshot, is_qa=qa))
        public = [{k: q[k] for k in ('id', 'category', 'title', 'question', 'options')} for q in snapshot]
        return {'token': token, 'version': VERSION, 'questions': public}

    def load(conn, token, lock=False):
        if len(token) < 40 or len(token) > 100:
            raise HTTPException(401, 'Accès au quiz non valide.')
        stmt = select(sessions).where(sessions.c.token_hash == digest(token))
        row = conn.execute(stmt.with_for_update() if lock else stmt).mappings().first()
        if not row or row['started_at'] < time.time() - 30 * 86400:
            raise HTTPException(401, 'Accès au quiz expiré ou non valide.')
        return row

    def auth(request):
        value = request.headers.get('authorization', '')
        return value[7:] if value.startswith('Bearer ') else ''

    @router.post('/api/faq/submit')
    def submit(data: Submit):
        with store.engine.begin() as conn:
            row = load(conn, data.token, lock=True)
            if row['result'] is not None:
                if row['answers'] != data.answers:
                    raise HTTPException(409, 'Le quiz a déjà été validé avec d’autres réponses.')
                return public_result(conn, row)
            questions = row['snapshot']
            if set(data.answers) != {q['id'] for q in questions} or any(
                    a < 0 or a > 3 for a in data.answers.values()):
                raise HTTPException(422, 'Réponds aux vingt questions avant de valider.')
            if not row['is_qa'] and time.time() - row['started_at'] < router.min_duration:
                raise HTTPException(429, 'Prends le temps de lire les questions avant de valider.')
            results = [dict(q, selected=data.answers[q['id']],
                       is_correct=data.answers[q['id']] == q['correct']) for q in questions]
            score = sum(q['is_correct'] for q in results)
            categories = {category: {'score': sum(q['is_correct'] for q in results if q['category'] == category),
                                    'total': 5} for category in dict.fromkeys(q['category'] for q in results)}
            result = {'score': score, 'total': 20, 'percentage': score * 5,
                      'categories': categories, 'results': results, 'version': VERSION}
            now = time.time()
            confirmation_token = secrets.token_urlsafe(36) if row['newsletter'] and not row['is_qa'] else None
            conn.execute(sessions.update().where(sessions.c.token_hash == row['token_hash']).values(
                completed_at=now, answers=data.answers, result=result,
                confirmation_hash=digest(confirmation_token) if confirmation_token else None))
            conn.execute(outbox.insert().values(token_hash=row['token_hash'], kind='results',
                payload={'token': data.token, 'confirmation_token': confirmation_token},
                status='pending', attempts=0, next_at=now))
            if router.notify_email and not row['is_qa']:
                conn.execute(outbox.insert().values(token_hash=row['token_hash'], kind='admin_notification',
                    payload={'to': router.notify_email}, status='pending', attempts=0, next_at=now))
            row = dict(row, result=result)
            return public_result(conn, row)

    @router.get('/api/faq/result')
    def result(request: Request):
        with store.engine.connect() as conn:
            row = load(conn, auth(request))
            if row['result'] is None:
                raise HTTPException(409, 'Le quiz n’est pas encore terminé.')
            return public_result(conn, row)

    @router.post('/api/faq/confirm')
    def confirm(request: Request):
        with store.engine.begin() as conn:
            token = auth(request)
            if len(token) < 40 or len(token) > 100:
                raise HTTPException(401, 'Lien de confirmation non valide.')
            row = conn.execute(select(sessions).where(sessions.c.confirmation_hash == digest(token))
                               .with_for_update()).mappings().first()
            if not row or row['started_at'] < time.time() - 30 * 86400:
                raise HTTPException(401, 'Lien de confirmation expiré ou non valide.')
            if row['is_qa']:
                raise HTTPException(403, 'Un test QA ne rejoint pas la liste de diffusion.')
            if not row['newsletter'] or row['result'] is None:
                raise HTTPException(403, 'Aucune inscription à confirmer pour ce quiz.')
            if not row['newsletter_confirmed']:
                conn.execute(sessions.update().where(sessions.c.token_hash == row['token_hash']).values(
                    newsletter_confirmed=True))
                conn.execute(outbox.insert().values(token_hash=row['token_hash'], kind='newsletter',
                    payload={}, status='pending', attempts=0, next_at=time.time()))
            return {'status': 'confirmation_received'}

    @router.get('/api/faq/admin/status')
    def admin_status(request: Request):
        if not router.admin_token or not hmac.compare_digest(
                request.headers.get('x-faq-admin', ''), router.admin_token):
            raise HTTPException(401, 'Accès refusé.')
        with store.engine.connect() as conn:
            rows = conn.execute(select(sessions.c.token_hash, sessions.c.started_at,
                sessions.c.completed_at, sessions.c.newsletter, sessions.c.newsletter_confirmed,
                sessions.c.is_qa).order_by(sessions.c.started_at.desc()).limit(30)).mappings().all()
            jobs = conn.execute(select(outbox.c.id, outbox.c.token_hash, outbox.c.kind,
                outbox.c.status, outbox.c.attempts, outbox.c.provider_id, outbox.c.last_error)
                .order_by(outbox.c.id.desc()).limit(60)).mappings().all()
        return {'sessions': [dict(r) for r in rows], 'jobs': [dict(r) for r in jobs]}

    @router.get('/api/faq/health')
    def health():
        with store.engine.connect() as conn:
            conn.execute(select(func.count()).select_from(sessions)).scalar_one()
        return {'status': 'ok', 'version': VERSION, 'storage': 'postgresql' if store.engine.dialect.name == 'postgresql' else 'sqlite',
                'questions': 20, 'mail_configured': bool(router.provider),
                'notifications_enabled': bool(router.notify_email)}

    return router
