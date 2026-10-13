import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.faq_api import build_router


@pytest.fixture
def client(tmp_path):
    app=FastAPI(); app.include_router(build_router('sqlite:///' + str(tmp_path/'security.db'),min_duration=0,admin_token='test-admin'))
    with TestClient(app) as c:
        yield c


def test_private_responses_are_not_cacheable(client):
    response=client.post('/api/faq/start',json={'email':'learner@example.com'})
    assert response.headers.get('cache-control') == 'no-store'


def test_invalid_emails_honeypots_and_unconsented_writes_fail_closed(client):
    assert client.post('/api/faq/start',json={'email':'bad-email'}).status_code==422
    assert client.post('/api/faq/start',json={'email':'learner@example.com','website':'spam'}).status_code==400
    assert client.get('/api/faq/admin/status').status_code==401
    assert client.get('/api/faq/result',headers={'Authorization':'Bearer '+ 'x'*48}).status_code==401
    d=client.post('/api/faq/start',json={'email':'learner@example.com'}).json()
    assert client.post('/api/faq/submit',json={'token':d['token'],'answers':{'1':0}}).status_code==422
    a={str(i):0 for i in range(1,21)};a['1']=True
    assert client.post('/api/faq/submit',json={'token':d['token'],'answers':a}).status_code==422
    a['1']=0
    assert client.post('/api/faq/submit',json={'token':d['token'],'answers':a}).status_code==200
    a['1']=1
    assert client.post('/api/faq/submit',json={'token':d['token'],'answers':a}).status_code==409
    assert client.post('/api/faq/confirm',headers={'Authorization':'Bearer '+d['token']}).status_code==401


def test_repeated_email_capture_is_limited(client):
    for _ in range(3):
        assert client.post('/api/faq/start',json={'email':'learner@example.com'}).status_code==200
    assert client.post('/api/faq/start',json={'email':'learner@example.com'}).status_code==429
