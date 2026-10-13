import importlib.util
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.faq_api import build_router, outbox


def test_results_worker_sends_twenty_explanations_once_and_reads_provider_receipt(tmp_path):
    assert importlib.util.find_spec('app.faq_delivery') is not None, 'Le worker de livraison manque'
    from app.faq_delivery import DeliveryWorker
    class Provider:
        calls = []
        reads = []
        def send_results(self, email, message):
            self.calls.append((email, message))
            assert message['html'].count('class="correction"') == 20
            assert 'BLOOD99' in message['html']
            assert '99 €' in message['html']
            return 'receipt-123'
        def verify_results(self, receipt):
            self.reads.append(receipt)
            return {'id': receipt, 'status': 'delivered'}
    provider = Provider()
    router = build_router('sqlite:///' + str(tmp_path / 'mail.db'), provider=provider, min_duration=0)
    app = FastAPI(); app.include_router(router)
    with TestClient(app) as client:
        d = client.post('/api/faq/start', json={'email': 'learner@example.com'}).json()
        client.post('/api/faq/submit', json={'token': d['token'], 'answers': {str(i): 0 for i in range(1,21)}})
        worker = DeliveryWorker(router.store, provider, 'https://quiz.example.com')
        assert worker.run_once() == 1
        assert worker.run_once() == 0
        assert len(provider.calls) == 1
        assert provider.reads == ['receipt-123']
        with router.store.engine.connect() as conn:
            job = conn.execute(select(outbox)).mappings().one()
            assert job['status'] == 'sent'
            assert job['provider_id'] == 'receipt-123'
            assert job['payload'] == {}, 'Les liens d’accès ne doivent pas rester dans la file après livraison'


def test_api_key_is_used_directly_without_reviving_obsolete_oauth_credentials():
    from app.faq_delivery import SendPulseProvider
    provider = SendPulseProvider('', '', 'coaching@achzodcoaching.com', api_key='sp_apikey_TEST')
    provider.authenticate()
    assert provider.http.headers['Authorization'] == 'Bearer sp_apikey_TEST'


def test_native_list_response_and_existing_contact_are_verified_without_reimport():
    from app.faq_delivery import SendPulseProvider
    provider = SendPulseProvider('', '', 'coaching@achzodcoaching.com')
    calls = []
    def transport(method, path, json_body=None, mutation=False):
        calls.append((method, path))
        if path == '/addressbooks/128647':
            return [{'id': 128647, 'name': 'My emails'}]
        return {'email': 'learner@example.com', 'status': 0}
    provider.request = transport
    assert provider.add_newsletter('learner@example.com', 0) == 'already_present'
    assert all(method == 'GET' for method, path in calls)


def test_pending_provider_readback_never_resends_an_accepted_mail(tmp_path):
    from app.faq_delivery import DeliveryWorker, ProviderError
    class Provider:
        sent = 0
        read = 0
        def send_results(self, email, message):
            self.sent += 1
            return 'known-receipt'
        def verify_results(self, receipt):
            self.read += 1
            if self.read == 1:
                raise ProviderError('smtp_receipt_not_visible')
            return {'id': receipt}
    provider = Provider()
    router = build_router('sqlite:///' + str(tmp_path / 'retry.db'), min_duration=0)
    app = FastAPI(); app.include_router(router)
    with TestClient(app) as client:
        d = client.post('/api/faq/start', json={'email': 'learner@example.com'}).json()
        client.post('/api/faq/submit', json={'token': d['token'], 'answers': {str(i): 0 for i in range(1,21)}})
    worker = DeliveryWorker(router.store, provider, 'https://quiz.example.com')
    worker.run_once()
    with router.store.engine.begin() as conn:
        job = conn.execute(select(outbox)).mappings().one()
        assert job['status'] == 'verify_pending'
        conn.execute(outbox.update().values(next_at=0))
    worker.run_once()
    assert provider.sent == 1
    assert provider.read == 2


def test_newsletter_accepted_but_not_yet_visible_is_verified_without_reimport(tmp_path):
    from app.faq_delivery import DeliveryWorker, ProviderError
    class Provider:
        adds=0
        verifications=0
        def send_results(self,email,message): return 'results-receipt'
        def verify_results(self,receipt): return {'id':receipt}
        def add_newsletter(self,email,consent_at):
            self.adds+=1
            raise ProviderError('newsletter_readback_pending', receipt='list:128647:accepted')
        def verify_newsletter(self,email):
            self.verifications+=1
            return 'added'
    provider=Provider();router=build_router('sqlite:///'+str(tmp_path/'newsletter.db'),min_duration=0)
    app=FastAPI();app.include_router(router)
    with TestClient(app) as client:
        d=client.post('/api/faq/start',json={'email':'learner@example.com','newsletter':True}).json()
        client.post('/api/faq/submit',json={'token':d['token'],'answers':{str(i):0 for i in range(1,21)}})
        with router.store.engine.connect() as conn:
            token=conn.execute(select(outbox)).mappings().one()['payload']['confirmation_token']
        client.post('/api/faq/confirm',headers={'Authorization':'Bearer '+token})
    worker=DeliveryWorker(router.store,provider,'https://quiz.example.com');worker.run_once();worker.run_once()
    with router.store.engine.begin() as conn:
        job=conn.execute(select(outbox).where(outbox.c.kind=='newsletter')).mappings().one()
        assert job['status']=='verify_pending'
        conn.execute(outbox.update().where(outbox.c.kind=='newsletter').values(next_at=0))
    worker.run_once()
    assert provider.adds==1 and provider.verifications==1
