import importlib.util
import pytest
from collections import Counter


def test_quiz_has_twenty_distinct_advanced_questions():
    assert importlib.util.find_spec('app.faq_content') is not None, 'Le nouveau contenu FAQ manque'
    from app.faq_content import QUESTIONS
    assert len(QUESTIONS) == 20
    assert len({q['id'] for q in QUESTIONS}) == 20
    assert sorted(Counter(q['category'] for q in QUESTIONS).values()) == [5, 5, 5, 5]
    for q in QUESTIONS:
        assert len(q['options']) == 4
        assert len(set(q['options'])) == 4
        assert type(q['correct']) is int and 0 <= q['correct'] <= 3
        assert len(q['explanation']) >= 180
        assert len(q['takeaway']) >= 25
        assert q['source']['url'].startswith('https://')


@pytest.mark.filterwarnings('error::DeprecationWarning')
def test_production_entrypoint_exposes_faq_without_breaking_the_legacy_quiz(tmp_path, monkeypatch):
    assert importlib.util.find_spec('app.faq_main') is not None, 'Le point d’entrée de production manque'
    monkeypatch.setenv('FAQ_DATABASE_URL', 'sqlite:///' + str(tmp_path / 'production.db'))
    from app.faq_main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        assert client.get('/faq').status_code == 200
        assert client.get('/api/faq/health').json()['questions'] == 20
        assert client.get('/').status_code == 200
        assert client.get('/api/health').status_code == 200


def test_start_captures_email_persistently_without_disclosing_answers(tmp_path):
    assert importlib.util.find_spec('app.faq_api') is not None, 'Le parcours persistant manque'
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.faq_api import build_router
    router = build_router('sqlite:///' + str(tmp_path / 'quiz.db'))
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        response = client.post('/api/faq/start', json={'email': 'reader@example.com', 'newsletter': False, 'website': ''})
        assert response.status_code == 200
        data = response.json()
        assert len(data['questions']) == 20
        assert len(data['token']) >= 40
        assert all(set(q) == {'id', 'category', 'title', 'question', 'options'} for q in data['questions'])
        with router.store.engine.connect() as conn:
            from sqlalchemy import text
            assert conn.execute(text('SELECT email FROM faq_sessions')).scalar_one() == 'reader@example.com'
