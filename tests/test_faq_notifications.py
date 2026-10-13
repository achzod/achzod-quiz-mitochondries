import importlib.util
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.faq_api import build_router, outbox, sessions, digest
from app.faq_delivery import DeliveryWorker


def test_completed_quiz_notifies_coach_once_with_participant_and_score(tmp_path):
    class Provider:
        deliveries=[]
        receipts=[]
        def send_results(self, email, message):
            self.deliveries.append((email,message))
            return 'mail-'+str(len(self.deliveries))
        def verify_results(self, receipt):
            self.receipts.append(receipt)
            return {'id':receipt}
    provider=Provider()
    router=build_router('sqlite:///'+str(tmp_path/'notifications.db'),min_duration=0,
                        notify_email='achzodyt@gmail.com')
    app=FastAPI();app.include_router(router)
    with TestClient(app) as client:
        d=client.post('/api/faq/start',json={'email':'learner@example.com'}).json()
        with router.store.engine.connect() as conn:
            row=conn.execute(select(sessions).where(sessions.c.token_hash==digest(d['token']))).mappings().one()
        answers={q['id']:q['correct'] for q in row['snapshot']}
        payload={'token':d['token'],'answers':answers}
        assert client.post('/api/faq/submit',json=payload).json()['score']==20
        assert client.post('/api/faq/submit',json=payload).status_code==200
    with router.store.engine.connect() as conn:
        jobs=list(conn.execute(select(outbox)).mappings())
        assert [j['kind'] for j in jobs]==['results','admin_notification']
    worker=DeliveryWorker(router.store,provider,'https://quiz.example.com')
    assert worker.run_once()==1
    assert worker.run_once()==1
    assert worker.run_once()==0
    assert len(provider.deliveries)==2
    recipient,message=provider.deliveries[1]
    assert recipient=='achzodyt@gmail.com'
    assert 'learner@example.com' in message['html']
    assert '20/20' in message['subject']
    for category in ['Métabolisme','Biomécanique','Nutrition','Compléments']:
        assert category in message['html']
    assert d['token'] not in message['html']
    assert provider.receipts==['mail-1','mail-2']


def test_qa_sessions_never_generate_coach_notifications(tmp_path):
    router=build_router('sqlite:///'+str(tmp_path/'qa-notify.db'),min_duration=0,
                        notify_email='achzodyt@gmail.com',admin_token='qa-secret')
    app=FastAPI();app.include_router(router)
    with TestClient(app) as client:
        d=client.post('/api/faq/start',json={'email':'qa@example.com'},headers={'X-FAQ-Admin':'qa-secret'}).json()
        client.post('/api/faq/submit',json={'token':d['token'],'answers':{str(i):0 for i in range(1,21)}})
    with router.store.engine.connect() as conn:
        assert list(conn.execute(select(outbox.c.kind)).scalars())==['results']
