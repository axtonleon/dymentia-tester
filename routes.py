from typing import Optional, List
from datetime import date
import base64

from fastapi import (
    APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, Body
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import services, schemas, models, ai_services
from database import get_db

# --- INITIALIZATION ---
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- PAGE RENDERING ROUTES ---

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    """Serves the main landing page."""
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/add-patient", response_class=HTMLResponse)
async def show_add_patient_form(request: Request):
    """Shows the form to add a new patient."""
    return templates.TemplateResponse("add_patient.html", {"request": request})

@router.get("/screening", response_class=HTMLResponse)
async def show_patient_list(request: Request, db: Session = Depends(get_db)):
    """Shows the list of all patients to choose from for screening."""
    patients = services.get_patients(db)
    return templates.TemplateResponse("patient_list.html", {"request": request, "patients": patients})

@router.get("/quiz/{patient_id}", response_class=HTMLResponse)
async def show_quiz_page(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = services.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return templates.TemplateResponse("quiz.html", {"request": request, "patient": patient})

# --- API ENDPOINTS ---

@router.post("/add-patient", response_model=schemas.Patient)
async def handle_add_patient(
    db: Session = Depends(get_db),
    patient_data: schemas.PatientCreate = Depends(services.patient_form_handler),
    image_files: dict = Depends(services.image_file_handler),
):
    """Handles the creation of a new patient from form data."""
    try:
        services.create_patient(db=db, patient_data=patient_data, image_files=image_files)
        return RedirectResponse(url="/screening", status_code=303)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/api/summarize-quiz", response_model=schemas.QuizSummary)
async def generate_quiz_summary_for_caregiver(
    request_data: schemas.QuizSummaryRequest, db: Session = Depends(get_db)
):
    """Accepts quiz results and returns a compassionate, LLM-generated summary."""
    patient = services.get_patient(db, request_data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        summary = ai_services.generate_quiz_summary(patient.first_name, request_data.results)
        total_score = sum(item.score for item in request_data.results)
        avg_score = total_score / len(request_data.results) if request_data.results else 0

        return {
            "summary": summary,
            "results": request_data.results,
            "average_score": avg_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.get("/api/quiz-questions/{patient_id}", response_model=List[schemas.QuizQuestion])
async def get_quiz_questions_for_patient(patient_id: int, db: Session = Depends(get_db)):
    """Returns a list of personalized quiz questions for a given patient."""
    patient = services.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_dict = {c.name: getattr(patient, c.name) for c in patient.__table__.columns}
    questions = services.generate_least_invasive_questions(patient_dict)
    
    return [
        {
            "question_text": q["question"],
            "reference_answer": str(q["answer"])
        }
        for q in questions
    ]
