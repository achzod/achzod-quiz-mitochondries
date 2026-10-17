"""Entrée de production : FAQ ajoutée, quiz historique inchangé."""
from contextlib import asynccontextmanager
import os
from app.main import app
from app.faq_api import build_router
from app.faq_content_v2 import QUESTIONS as QUIZ_TWO, VERSION as QUIZ_TWO_VERSION
from app.faq_delivery import SendPulseProvider, DeliveryWorker

provider = None
api_key = os.environ.get('FAQ_SENDPULSE_API_KEY')
if api_key:
    provider = SendPulseProvider('', '', os.environ.get('FAQ_SENDER_EMAIL', 'coaching@achzodcoaching.com'),
        os.environ.get('FAQ_SENDER_NAME', 'Achzod'), api_key=api_key)
if os.environ.get('RENDER') and (not provider or not os.environ.get('FAQ_SECRET') or not os.environ.get('FAQ_ADMIN_TOKEN')):
    raise RuntimeError('FAQ_PRODUCTION_CONFIG_REQUIRED')

router = build_router(provider=provider)
app.include_router(router)
app.include_router(build_router(provider=provider, question_bank=QUIZ_TWO,
                                version=QUIZ_TWO_VERSION, prefix='/quiz-2',
                                page_template='faq2.html'))
worker = DeliveryWorker(router.store, provider, router.public_url) if provider else None

@asynccontextmanager
async def lifespan(application):
    if worker:
        worker.start()
    yield
    if worker:
        worker.stop()

app.router.lifespan_context = lifespan
