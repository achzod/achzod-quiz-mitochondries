"""
Serveur FastAPI pour le quiz Mitochondries Achzod
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import logging
from datetime import datetime

from app.questions import get_all_questions, get_question_by_id
from app.email_sender import send_quiz_results

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz Mitochondries Achzod")

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Stockage en mémoire des sessions de quiz
quiz_sessions: Dict[str, dict] = {}


class QuizAnswer(BaseModel):
    session_id: str
    question_id: int
    selected_option: int


class QuizSubmit(BaseModel):
    session_id: str
    email: str
    answers: Dict[str, int]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Page d'accueil du quiz"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/quiz/start")
async def start_quiz():
    """Démarre une nouvelle session de quiz"""
    session_id = str(uuid.uuid4())
    questions = get_all_questions()

    quiz_sessions[session_id] = {
        "started_at": datetime.now().isoformat(),
        "answers": {},
        "questions": questions
    }

    logger.info(f"[QUIZ START] session_id={session_id} total_questions={len(questions)}")

    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "questions": questions
    }


@app.post("/api/quiz/submit")
async def submit_quiz(data: QuizSubmit):
    """
    Soumet le quiz complet et calcule le score
    """
    if data.session_id not in quiz_sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session non trouvée"}
        )

    session = quiz_sessions[data.session_id]
    questions = get_all_questions()

    # Calcul du score
    correct_answers = 0
    total_questions = len(questions)
    results = []

    for question in questions:
        qid = str(question["id"])
        user_answer = data.answers.get(qid, -1)
        is_correct = (user_answer == question["correct"])

        if is_correct:
            correct_answers += 1

        results.append({
            "question_id": question["id"],
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["correct"],
            "is_correct": is_correct,
            "explanation": question["explanation"],
            "options": question["options"]
        })

    score_percentage = (correct_answers / total_questions) * 100

    logger.info(
        f"[QUIZ SUBMIT] session_id={data.session_id} email={data.email} "
        f"score={correct_answers}/{total_questions} ({score_percentage:.1f}%)"
    )

    # Envoi de l'email avec les résultats
    email_sent = send_quiz_results(
        email=data.email,
        score=correct_answers,
        total=total_questions,
        percentage=score_percentage,
        results=results
    )

    if email_sent:
        logger.info(f"[EMAIL SUCCESS] Quiz results sent to {data.email}")
    else:
        logger.warning(f"[EMAIL FAILED] Could not send results to {data.email}")

    return {
        "session_id": data.session_id,
        "score": correct_answers,
        "total": total_questions,
        "percentage": score_percentage,
        "results": results,
        "email_sent": email_sent
    }


@app.get("/api/health")
async def health():
    """Endpoint de santé"""
    return {
        "status": "ok",
        "active_sessions": len(quiz_sessions)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
