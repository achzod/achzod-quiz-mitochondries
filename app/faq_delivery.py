"""Livraison durable des corrigés FAQ et inscription consentie à SendPulse."""
import base64
from datetime import datetime, timezone
from html import escape
import json
import logging
import os
import threading
import time
from urllib.parse import quote

import requests
from sqlalchemy import select, delete, or_
from app.faq_api import sessions, outbox
from app.faq_notifications import render_admin_notification

log = logging.getLogger(__name__)


class ProviderError(Exception):
    def __init__(self, code, uncertain=False, permanent=False, receipt=None):
        super().__init__(code)
        self.uncertain = uncertain
        self.permanent = permanent
        self.receipt = receipt


def render_email(row, payload, public_url):
    result = row['result']
    url = public_url.rstrip('/') + '/faq#result=' + quote(payload['token'], safe='')
    parts = []
    text = [f"Ton score : {result['score']}/20", 'Les 20 réponses et leurs explications :', '']
    for i, q in enumerate(result['results'], 1):
        chosen, right = q['options'][q['selected']], q['options'][q['correct']]
        parts.append(f'''<tr><td class="correction" style="padding:25px 0;border-top:1px solid #d9dccf;">
        <p style="font:700 11px Arial,sans-serif;color:#64685e;letter-spacing:1px;margin:0 0 8px;">{i:02d} / {escape(q['category'])}</p>
        <h2 style="font:700 21px/1.3 Arial,sans-serif;color:#171916;margin:0 0 14px;">{escape(q['title'])}</h2>
        <p style="font:15px/1.65 Arial,sans-serif;color:#171916;margin:0 0 15px;">{escape(q['question'])}</p>
        <p style="font:14px/1.6 Arial,sans-serif;color:#171916;margin:0 0 10px;"><b>Ton choix :</b> {escape(chosen)} {'✓' if q['is_correct'] else '· À revoir'}</p>
        <p style="font:14px/1.6 Arial,sans-serif;color:#1e4b32;background:#e7eddf;padding:12px;margin:0 0 18px;"><b>Bonne réponse :</b> {escape(right)}</p>
        <p style="font:15px/1.7 Arial,sans-serif;color:#171916;margin:0 0 15px;">{escape(q['explanation'])}</p>
        <p style="font:700 15px/1.6 Arial,sans-serif;color:#171916;margin:0 0 14px;">{escape(q['takeaway'])}</p>
        <p style="font:12px/1.6 Arial,sans-serif;color:#64685e;margin:0;">Source : <a href="{escape(q['source']['url'], quote=True)}" style="color:#315339;">{escape(q['source']['title'])}</a></p>
        </td></tr>''')
        text.extend([f"{i}. {q['title']}", q['question'], 'Ton choix : ' + chosen,
                     'Bonne réponse : ' + right, q['explanation'], q['takeaway'],
                     q['source']['title'] + ' · ' + q['source']['url'], ''])
    confirmation = ''
    if payload.get('confirmation_token'):
        confirm_url = public_url.rstrip('/') + '/faq#confirm=' + quote(payload['confirmation_token'], safe='')
        confirmation = f'''<tr><td style="padding:24px 0;border-top:1px solid #d9dccf;"><p style="font:700 17px Arial,sans-serif;color:#171916;">Tu as choisi de recevoir les prochains contenus.</p><p style="font:14px/1.6 Arial,sans-serif;color:#64685e;">Un clic de confirmation reste nécessaire. Ce choix est indépendant de ton corrigé.</p><a href="{escape(confirm_url, quote=True)}" style="display:inline-block;background:#171916;color:#fff;padding:14px 22px;text-decoration:none;font:700 14px Arial,sans-serif;">Confirmer mon inscription →</a></td></tr>'''
        text.extend(['Confirmer les prochains contenus (facultatif) : ' + confirm_url, ''])
    category_text = ' · '.join(f"{c} : {v['score']}/{v['total']}" for c,v in result['categories'].items())
    body = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>Ton corrigé FAQ Achzod</title></head><body style="margin:0;background:#f5f3eb;color:#171916;"><div style="display:none;max-height:0;overflow:hidden;opacity:0;">Ton score, les 20 réponses expliquées et les sources pour aller plus loin.</div><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f5f3eb;"><tr><td align="center" style="padding:26px 14px;"><table role="presentation" width="620" cellspacing="0" cellpadding="0" style="width:100%;max-width:620px;background:#fffef9;"><tr><td style="padding:28px 24px;"><p style="font:900 24px Arial,sans-serif;letter-spacing:-1px;margin:0 0 35px;color:#171916;">ACHZOD.</p><p style="font:700 11px Arial,sans-serif;color:#315339;letter-spacing:1px;margin:0 0 14px;">FAQ LAB / TON CORRIGÉ</p><h1 style="font:900 36px/1.12 Arial,sans-serif;color:#171916;letter-spacing:-1px;margin:0 0 20px;">{result['score']} bonnes réponses.<br>20 occasions de comprendre.</h1><p style="font:15px/1.7 Arial,sans-serif;color:#171916;margin:0 0 18px;">Tu as terminé le quiz. Le plus intéressant, maintenant, c’est de voir pourquoi une réponse tient et pourquoi les autres ne tiennent pas.</p><p style="font:700 13px/1.8 Arial,sans-serif;color:#171916;background:#f1d548;padding:16px;margin:0 0 22px;">{escape(category_text)}</p><p style="font:14px/1.6 Arial,sans-serif;color:#64685e;margin:0 0 25px;">Ton score porte sur ces vingt questions. Ce n’est ni une évaluation de ta santé, ni une mesure de ton potentiel physique.</p><a href="{escape(url, quote=True)}" style="display:inline-block;background:#171916;color:#fff;padding:14px 22px;font:700 14px Arial,sans-serif;text-decoration:none;">Ouvrir mon corrigé interactif →</a><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-top:30px;">{''.join(parts)}{confirmation}<tr><td style="padding:25px 20px;background:#f1d548;"><h2 style="font:700 23px/1.3 Arial,sans-serif;color:#171916;margin:0 0 12px;">La théorie est utile. Ton plan doit parler de toi.</h2><p style="font:15px/1.65 Arial,sans-serif;color:#171916;margin:0 0 18px;">Pour passer à un coaching adapté à ton objectif et à tes contraintes : <b>99 € de réduction avec le code BLOOD99.</b></p><a href="https://www.achzodcoaching.com/" style="display:inline-block;background:#171916;color:#fff;padding:14px 22px;font:700 14px Arial,sans-serif;text-decoration:none;">Découvrir les coachings →</a></td></tr></table><p style="font:12px/1.7 Arial,sans-serif;color:#64685e;margin:24px 0 0;">Ce mail répond à ta participation au quiz. Il ne t’inscrit pas automatiquement à la newsletter. Les données du quiz et son lien d’accès sont conservés 30 jours. Pour tes données : coaching@achzodcoaching.com. Garde ce lien personnel pour toi.</p></td></tr></table></td></tr></table></body></html>'''
    text.extend(['Découvrir les coachings : https://www.achzodcoaching.com/',
                 'BLOOD99 : 99 € de réduction.', 'Ton corrigé interactif : ' + url,
                 'Données du quiz : conservation 30 jours. Contact : coaching@achzodcoaching.com.'])
    return {'subject': f"Ton score : {result['score']}/20 · Les 20 réponses expliquées — Achzod",
            'html': body, 'text': '\n'.join(text)}


class SendPulseProvider:
    def __init__(self, client_id, client_secret, sender_email, sender_name='Achzod', list_id=128647, api_key=None):
        self.client_id, self.client_secret = client_id, client_secret
        self.api_key = api_key
        self.sender_email, self.sender_name, self.list_id = sender_email, sender_name, int(list_id)
        self.http = requests.Session()
        self.token_expiry = 0
        self.api = 'https://api.sendpulse.com'

    def authenticate(self):
        if self.api_key:
            self.http.headers['Authorization'] = 'Bearer ' + self.api_key
            return
        if self.token_expiry > time.time():
            return
        try:
            r = self.http.post(self.api + '/oauth/access_token', json={'grant_type': 'client_credentials',
                'client_id': self.client_id, 'client_secret': self.client_secret}, timeout=(5,20))
        except requests.RequestException:
            raise ProviderError('oauth_unavailable')
        if r.status_code != 200:
            raise ProviderError('oauth_http_' + str(r.status_code), permanent=r.status_code in (401,403))
        token = r.json().get('access_token')
        if not token:
            raise ProviderError('oauth_missing_token', permanent=True)
        self.http.headers['Authorization'] = 'Bearer ' + token
        self.token_expiry = time.time() + 3000

    def request(self, method, path, json_body=None, mutation=False):
        self.authenticate()
        try:
            r = self.http.request(method, self.api + path, json=json_body, timeout=(5,25))
        except requests.RequestException:
            raise ProviderError('provider_network', uncertain=mutation)
        if r.status_code == 401:
            self.token_expiry = 0
        if r.status_code >= 400:
            raise ProviderError('provider_http_' + str(r.status_code),
                                uncertain=mutation and r.status_code >= 500,
                                permanent=r.status_code in (400,401,403,422))
        try:
            return r.json()
        except ValueError:
            raise ProviderError('provider_invalid_response', uncertain=mutation)

    def send_results(self, email, message):
        email_body = {'subject': message['subject'], 'html': base64.b64encode(message['html'].encode()).decode(),
            'text': message['text'], 'from': {'name': self.sender_name, 'email': self.sender_email},
            'to': [{'email': email}], 'bcc': [], 'cc': []}
        response = self.request('POST', '/smtp/emails', {'email': email_body}, mutation=True)
        receipt = response.get('id')
        if not response.get('result') or not receipt:
            raise ProviderError('smtp_missing_receipt', uncertain=True)
        return str(receipt)

    def verify_results(self, receipt):
        data = self.request('GET', '/smtp/emails/' + quote(receipt, safe=''))
        if not isinstance(data, dict) or str(data.get('id', '')) != receipt:
            raise ProviderError('smtp_receipt_not_visible')
        return data

    def add_newsletter(self, email, consent_at):
        book = self.request('GET', '/addressbooks/' + str(self.list_id))
        if isinstance(book, list):
            book = book[0] if len(book) == 1 else {}
        if str(book.get('id')) != str(self.list_id) or book.get('name') != 'My emails':
            raise ProviderError('addressbook_identity_mismatch', permanent=True)
        path = '/addressbooks/' + str(self.list_id) + '/emails/' + quote(email, safe='')
        try:
            existing = self.request('GET', path)
        except ProviderError as exc:
            if str(exc) != 'provider_http_404':
                raise
            existing = None
        if existing and existing.get('email'):
            if existing.get('status') not in (0, '0', 'active'):
                return 'skipped_optout'
            return 'already_present'
        response = self.request('POST', '/addressbooks/' + str(self.list_id) + '/emails',
            {'emails': [{'email': email, 'variables': {'source': 'FAQ20 Achzod',
                'faq_consent_at': datetime.fromtimestamp(consent_at, timezone.utc).isoformat()}}]}, mutation=True)
        if not response.get('result'):
            raise ProviderError('newsletter_add_not_confirmed', uncertain=True)
        try:
            return self.verify_newsletter(email)
        except ProviderError:
            # Le fournisseur a accepté l’import : seules des lectures suivent.
            raise ProviderError('newsletter_readback_pending', receipt='list:128647:accepted')

    def verify_newsletter(self, email):
        check = self.request('GET', '/addressbooks/' + str(self.list_id) + '/emails/' + quote(email, safe=''))
        if str(check.get('email','')).lower() != email.lower() or str(check.get('abook_id')) != str(self.list_id):
            raise ProviderError('newsletter_readback_mismatch', uncertain=True)
        return 'added' if check.get('status') in (0, '0', 'active') else 'skipped_optout'


class DeliveryWorker:
    def __init__(self, store, provider, public_url):
        self.store, self.provider, self.public_url = store, provider, public_url
        self.stop_event = threading.Event()
        self.thread = None

    def run_once(self):
        now = time.time()
        with self.store.engine.begin() as conn:
            # Un envoi interrompu sans reçu est ambigu : pas de renvoi automatique.
            conn.execute(outbox.update().where(outbox.c.status == 'processing', outbox.c.lease_at < now-180)
                .values(status='needs_review', last_error='interrupted_delivery'))
            stmt = select(outbox).where(outbox.c.status.in_(['pending','verify_pending']), outbox.c.next_at <= now)
            job = conn.execute(stmt.order_by(outbox.c.id).limit(1)).mappings().first()
            if not job:
                return 0
            changed = conn.execute(outbox.update().where(outbox.c.id == job['id'], outbox.c.status == job['status'])
                .values(status='processing', lease_at=now, attempts=job['attempts']+1)).rowcount
            if not changed:
                return 0
            row = conn.execute(select(sessions).where(sessions.c.token_hash == job['token_hash'])).mappings().one()
        status, receipt, outcome = 'sent', job['provider_id'], None
        try:
            if job['kind'] in ('results', 'admin_notification'):
                if not receipt:
                    if job['kind'] == 'results':
                        message = render_email(row, job['payload'], self.public_url)
                        recipient = row['email']
                    else:
                        message = render_admin_notification(row, self.public_url)
                        recipient = job['payload']['to']
                    receipt = self.provider.send_results(recipient, message)
                    with self.store.engine.begin() as conn:
                        conn.execute(outbox.update().where(outbox.c.id == job['id']).values(provider_id=receipt))
                self.provider.verify_results(receipt)
            elif job['kind'] == 'newsletter':
                outcome = (self.provider.verify_newsletter(row['email']) if receipt else
                           self.provider.add_newsletter(row['email'], row['completed_at']))
                status = 'skipped_optout' if outcome == 'skipped_optout' else 'sent'
                receipt = 'list:128647:' + outcome
            else:
                raise ProviderError('unknown_job', permanent=True)
        except ProviderError as exc:
            receipt = exc.receipt or receipt
            status = ('verify_pending' if receipt else
                      'needs_review' if exc.uncertain else 'blocked_provider' if exc.permanent else
                      'failed' if job['attempts'] >= 4 else 'pending')
            with self.store.engine.begin() as conn:
                conn.execute(outbox.update().where(outbox.c.id == job['id']).values(status=status,
                    next_at=now + min(3600, 60*2**job['attempts']), lease_at=None,
                    provider_id=receipt, last_error=str(exc)[:80]))
            log.warning('FAQ_DELIVERY job=%s status=%s code=%s', job['id'], status, str(exc))
            return 1
        with self.store.engine.begin() as conn:
            conn.execute(outbox.update().where(outbox.c.id == job['id']).values(status=status,
                provider_id=receipt, payload={}, lease_at=None, last_error=None))
        log.info('FAQ_DELIVERY job=%s status=%s', job['id'], status)
        return 1

    def cleanup(self):
        cutoff = time.time() - 30*86400
        with self.store.engine.begin() as conn:
            expired = select(sessions.c.token_hash).where(sessions.c.started_at < cutoff)
            conn.execute(delete(outbox).where(outbox.c.token_hash.in_(expired)))
            conn.execute(delete(sessions).where(sessions.c.started_at < cutoff))

    def start(self):
        def loop():
            last_cleanup = 0
            while not self.stop_event.is_set():
                try:
                    if time.time()-last_cleanup > 3600:
                        self.cleanup();last_cleanup=time.time()
                    processed=self.run_once()
                except Exception:
                    # Pas de log d’email, de corps de message ou de token.
                    log.error('FAQ_WORKER_UNEXPECTED_ERROR')
                    processed=0
                self.stop_event.wait(1 if processed else 3)
        self.thread = threading.Thread(target=loop, name='faq-delivery', daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=35)
