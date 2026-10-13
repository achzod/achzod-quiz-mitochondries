import importlib.util
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select


@pytest.fixture
def flow(tmp_path):
    from app.faq_api import build_router
    router = build_router('sqlite:///' + str(tmp_path / 'flow.db'), min_duration=0, admin_token='qa-secret')
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        yield client, router


def begin(client, newsletter=False, headers=None):
    return client.post('/api/faq/start', json={'email': 'learner@example.com', 'newsletter': newsletter}, headers=headers or {}).json()


def correct_answers(router, token):
    from app.faq_api import sessions, digest
    with router.store.engine.connect() as conn:
        row = conn.execute(select(sessions).where(sessions.c.token_hash == digest(token))).mappings().one()
    return {q['id']: q['correct'] for q in row['snapshot']}


def test_complete_flow_is_persistent_idempotent_and_requires_newsletter_confirmation(flow):
    client, router = flow
    data = begin(client, newsletter=True)
    token = data['token']
    payload = {'token': token, 'answers': correct_answers(router, token)}
    r = client.post('/api/faq/submit', json=payload)
    assert r.status_code == 200, 'Le corrigé et la file persistante manquent'
    assert r.json()['score'] == 20
    assert len(r.json()['results']) == 20
    assert r.json()['newsletter_status'] == 'confirmation_required'
    assert client.post('/api/faq/submit', json=payload).json()['score'] == 20
    from app.faq_api import outbox
    with router.store.engine.connect() as conn:
        rows = list(conn.execute(select(outbox)).mappings())
    assert [r['kind'] for r in rows] == ['results']
    assert client.post('/api/faq/confirm', headers={'Authorization': 'Bearer ' + token}).status_code == 401
    confirmation_token = rows[0]['payload']['confirmation_token']
    assert confirmation_token != token
    r = client.post('/api/faq/confirm', headers={'Authorization': 'Bearer ' + confirmation_token})
    assert r.status_code == 200
    assert client.post('/api/faq/confirm', headers={'Authorization': 'Bearer ' + confirmation_token}).status_code == 200
    with router.store.engine.connect() as conn:
        assert sorted(conn.execute(select(outbox.c.kind)).scalars()) == ['newsletter', 'results']
    restored = client.get('/api/faq/result', headers={'Authorization': 'Bearer ' + token})
    assert restored.json()['score'] == 20


def test_public_quiz_page_is_accessible_and_keeps_marketing_optional(flow):
    client, router = flow
    response = client.get('/faq')
    assert response.status_code == 200, 'L’interface FAQ manque'
    assert 'BLOOD99' in response.text
    assert 'name="newsletter"' in response.text
    assert 'id="quiz-app"' in response.text
    assert 'name="newsletter" checked' not in response.text
