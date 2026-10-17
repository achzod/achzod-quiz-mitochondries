from collections import Counter
import importlib.util


def test_second_quiz_has_twenty_original_sourced_cases():
    assert importlib.util.find_spec('app.faq_content_v2') is not None, 'Quiz 2 content is missing'
    from app.faq_content import QUESTIONS as OLD
    from app.faq_content_v2 import QUESTIONS, VERSION, CATEGORIES
    assert VERSION != 'faq-2026-10-v1'
    assert len(QUESTIONS) == len({q['id'] for q in QUESTIONS}) == 20
    assert Counter(q['category'] for q in QUESTIONS) == {c:5 for c in CATEGORIES}
    assert len(CATEGORIES) == 4
    assert not {q['question'] for q in OLD}.intersection(q['question'] for q in QUESTIONS)
    for q in QUESTIONS:
        assert len(q['options']) == len(set(q['options'])) == 4
        assert type(q['correct']) is int and 0 <= q['correct'] < 4
        assert len(q['explanation']) >= 350
        assert len(q['takeaway']) >= 35
        assert q['source']['url'].startswith('https://pubmed.ncbi.nlm.nih.gov/')


def test_two_quizzes_keep_snapshots_scores_and_legacy_sessions_separate(tmp_path):
    import inspect
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy import select
    from app.faq_api import build_router, sessions, digest
    from app.faq_content_v2 import QUESTIONS, VERSION
    assert 'question_bank' in inspect.signature(build_router).parameters, 'Versioned quiz router is missing'
    db='sqlite:///'+str(tmp_path/'both.db')
    old=build_router(db,min_duration=0)
    new=build_router(db,min_duration=0,question_bank=QUESTIONS,version=VERSION,prefix='/quiz-2',page_template='faq2.html')
    app=FastAPI();app.include_router(old);app.include_router(new)
    with TestClient(app) as client:
        first=client.post('/api/faq/start',json={'email':'old@example.com'}).json()
        second=client.post('/quiz-2/api/faq/start',json={'email':'new@example.com'}).json()
        assert first['version']!=second['version']==VERSION
        assert {q['id'] for q in first['questions']}.isdisjoint(q['id'] for q in second['questions'])
        assert all(set(q)=={'id','category','title','question','options'} for q in second['questions'])
        with old.store.engine.begin() as conn:
            row=conn.execute(select(sessions).where(sessions.c.token_hash==digest(first['token']))).mappings().one()
            legacy=[{k:v for k,v in q.items() if not k.startswith('_quiz_')} for q in row['snapshot']]
            conn.execute(sessions.update().where(sessions.c.token_hash==row['token_hash']).values(snapshot=legacy))
            row2=conn.execute(select(sessions).where(sessions.c.token_hash==digest(second['token']))).mappings().one()
            right={q['id']:q['correct'] for q in row2['snapshot']}
        saved=client.post('/quiz-2/api/faq/submit',json={'token':second['token'],'answers':right}).json()
        assert saved['score']==20 and saved['quiz_path']=='/quiz-2/faq' and saved['version']==VERSION
        assert client.post('/quiz-2/api/faq/submit',json={'token':second['token'],'answers':right}).json()==saved
        cross=client.post('/quiz-2/api/faq/submit',json={'token':first['token'],'answers':{q['id']:0 for q in first['questions']}}).json()
        assert cross['version']=='faq-2026-10-v1' and cross['quiz_path']=='/faq'
        assert client.get('/api/faq/health').json()['version']=='faq-2026-10-v1'
        assert client.get('/quiz-2/api/faq/health').json()['version']==VERSION


def test_quiz_two_email_links_back_to_its_quiz_without_unverified_promo():
    import copy
    from app.faq_content_v2 import QUESTIONS, VERSION
    from app.faq_delivery import render_email
    questions=[dict(copy.deepcopy(q),selected=q['correct'],is_correct=True) for q in QUESTIONS]
    result={'version':VERSION,'score':20,'categories':{q['category']:{'score':5,'total':5} for q in QUESTIONS},'results':questions,'quiz_path':'/quiz-2/faq'}
    message=render_email({'result':result},{'token':'private-token','confirmation_token':'confirmation-token'},'https://quiz.example.com')
    assert 'https://quiz.example.com/quiz-2/faq#result=private-token' in message['html']
    assert 'https://quiz.example.com/quiz-2/faq#confirm=confirmation-token' in message['html']
    assert 'BLOOD99' not in message['html']+message['text']
    assert message['html'].count('class="correction"')==20
    assert 'Quiz 02' in message['subject']


def test_production_serves_both_quizzes_with_distinct_frontend_storage(tmp_path,monkeypatch):
    monkeypatch.setenv('FAQ_DATABASE_URL','sqlite:///'+str(tmp_path/'prod.db'))
    from app.faq_main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        response=client.get('/quiz-2/faq')
        assert response.status_code==200, 'Second public quiz is not mounted'
        text=response.text
        assert 'QUIZ 02' in text and 'achzod-faq-v2' in text
        assert "'/quiz-2/api/faq/start'" in text
        assert 'BLOOD99' not in text
        import ast,re
        from app.faq_content_v2 import CATEGORIES
        match=re.search(r'const categories=(\[.*?\]);',text)
        assert match is not None
        assert ast.literal_eval(match.group(1))==CATEGORIES
        assert 'achzod-faq-v1' in client.get('/faq').text
        assert client.get('/quiz-2/api/faq/health').json()['version']=='faq-2026-10-v2'
