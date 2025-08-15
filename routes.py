from typing import List
import base64
import secrets
import os
import random

from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, Query
)
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

import services, schemas, models, ai_services
from database import get_db
from dependencies import templates

# --- INITIALIZATION ---
router = APIRouter()

# --- PAGE RENDERING ROUTES ---

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    """Serves the main landing page."""
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/add-question", response_class=HTMLResponse)
async def show_add_question_form(request: Request):
    """Shows the form to add a new question."""
    return templates.TemplateResponse("add_question.html", {"request": request})

@router.post("/add-question", response_class=HTMLResponse)
async def handle_add_question(
    request: Request,
    image: UploadFile = File(...),
    question: str = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db)
):
    # Save the image
    file_extension = image.filename.split(".")[-1]
    image_filename = f"{secrets.token_hex(16)}.{file_extension}"
    image_path = os.path.join("static/uploads", image_filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())

    # Create a new question
    question_data = schemas.QuestionCreate(question=question, answer=answer, image_path=image_filename)
    services.create_question(db=db, question=question_data, image_path=image_filename)

    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/quiz", response_class=HTMLResponse)
async def show_quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})

@router.get("/questions", response_class=HTMLResponse)
async def show_questions_page(request: Request, db: Session = Depends(get_db)):
    questions = services.get_questions(db)
    return templates.TemplateResponse("view_questions.html", {"request": request, "questions": questions})

@router.post("/question/{question_id}/edit", response_class=HTMLResponse)
async def handle_edit_question(
    request: Request,
    question_id: int,
    question: str = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db)
):
    question_data = schemas.QuestionUpdate(question=question, answer=answer)
    services.update_question(db=db, question_id=question_id, question_data=question_data)
    questions = services.get_questions(db)
    return templates.TemplateResponse("view_questions.html", {"request": request, "questions": questions})

@router.get("/question/{question_id}/delete", response_class=HTMLResponse)
async def handle_delete_question(
    request: Request,
    question_id: int,
    db: Session = Depends(get_db)
):
    services.delete_question(db=db, question_id=question_id)
    questions = services.get_questions(db)
    return templates.TemplateResponse("view_questions.html", {"request": request, "questions": questions})


# --- API ENDPOINTS ---

@router.get("/api/quiz-questions", response_model=List[schemas.Question])
async def get_quiz_questions(count: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    questions = services.get_questions(db)
    if len(questions) < count:
        raise HTTPException(status_code=404, detail=f"Not enough questions in the database to start a quiz with {count} questions.")
    return random.sample(questions, count)

@router.post("/api/text-to-speech")
async def convert_text_to_speech(data: schemas.TextToSpeechRequest):
    """Converts text to speech and returns an MP3 audio stream."""
    try:
        audio_stream = ai_services.generate_question_audio(data.text)
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

@router.post("/api/submit-answer", response_model=schemas.EvaluationResult)
async def transcribe_and_evaluate_answer(
    response_time: float = Form(...),
    reference_answer_b64: str = Form(...),
    file: UploadFile = File(...)
):
    """Transcribes audio, evaluates it, and returns the result."""
    try:
        user_answer_text = ai_services.transcribe_audio_file(file.file)
        reference_answer = base64.b64decode(reference_answer_b64).decode("utf-8")
        evaluation_result = ai_services.evaluate_answer(reference_answer, user_answer_text)
        
        return {
            "transcribed_text": user_answer_text,
            "response_time": round(response_time, 2),
            "score": evaluation_result.score,
            "feedback": evaluation_result.feedback,
            "reference_answer": reference_answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/api/summarize-quiz", response_model=schemas.QuizSummary)
async def generate_quiz_summary(
    request_data: schemas.QuizSummaryRequest, db: Session = Depends(get_db)
):
    """Accepts quiz results and returns a compassionate, LLM-generated summary."""
    print(f"Received quiz summary request: {request_data}")
    try:
        summary = ai_services.generate_quiz_summary("Patient", request_data.results)
        total_score = sum(item.score for item in request_data.results)

        # Handle response times safely - some results might not have response_time
        response_times = [getattr(item, 'response_time', 0.0) for item in request_data.results]
        total_response_time = sum(response_times)

        avg_score = total_score / len(request_data.results) if request_data.results else 0
        avg_response_time = total_response_time / len(response_times) if response_times else 0

        return {
            "summary": summary,
            "results": request_data.results,
            "average_score": avg_score,
            "average_response_time": avg_response_time
        }
    except Exception as e:
        print(f"Error in generate_quiz_summary: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.get("/api/questions/count")
def get_questions_count(db: Session = Depends(get_db)):
    return {"total_questions": services.get_questions_count(db)}