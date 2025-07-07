# services.py
import os
import uuid
from typing import List, Dict, Optional
from datetime import date

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, Form, File

import models, schemas

UPLOAD_DIR = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> Optional[str]:
    """Validates and saves an uploaded file, returning its server path."""
    if not upload_file or not upload_file.filename:
        return None

    file_extension = upload_file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return f"/{file_path}"

def create_patient(db: Session, patient_data: schemas.PatientCreate, image_files: Dict) -> models.Patient:
    """Creates a new patient, calculates BMI, and saves associated images."""
    patient_dict = patient_data.dict()
    weight_kg = patient_dict.get("weight")
    height_cm = patient_dict.get("height")
    if weight_kg and height_cm and height_cm > 0:
        height_m = height_cm / 100
        patient_dict["bmi"] = round(weight_kg / (height_m * height_m), 2)

    db_patient = models.Patient(**patient_dict)

    for field, file in image_files.items():
        if file and file.filename:
            setattr(db_patient, f"{field}_path", save_upload_file(file))

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    """Retrieves a single patient by their ID."""
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session) -> List[models.Patient]:
    """Retrieves all patient records from the database."""
    return db.query(models.Patient).order_by(models.Patient.id).all()

def generate_least_invasive_questions(patient: dict) -> list:
    """
    Generate up to 10 quiz questions from the least invasive patient fields that have non-empty answers.
    Returns a list of dicts: {field, question, answer}
    """
    field_questions = [
        ("first_name", "What is your first name?"),
        ("hobbies", "What is one of your hobbies?"),
        ("favorite_foods", "What is your favorite food?"),
        ("preferred_drinks", "What is your preferred drink?"),
        ("favorite_activities", "What is one of your favorite activities?"),
        ("former_profession", "What was your former profession?"),
        ("preferred_music_genre", "What is your favorite music genre?"),
        ("favorite_color", "What is your favorite color?"),
        ("pet_image_path", "Do you have a pet? Can you describe it or its name?"),
        ("car_image_path", "Can you describe your car or a memorable car you had?"),
        ("house_image_path", "Can you describe your house or a memorable house?"),
        ("country", "Which country are you from?"),
        ("education_level", "What is your highest level of education?"),
        ("languages_spoken", "What languages do you speak?"),
        ("favorite_smells", "What is a smell you like?"),
        ("preferred_clothing_type", "What type of clothing do you prefer?"),
        ("preferred_social_activity", "What is your favorite social activity?")
    ]
    questions = []
    for field, question in field_questions:
        value = patient.get(field)
        if value not in (None, "", [], {}):
            questions.append({"field": field, "question": question, "answer": value})
        if len(questions) == 10:
            break
    return questions

def patient_form_handler(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: Optional[date] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    emergency_contact_name: Optional[str] = Form(None),
    emergency_contact_relationship: Optional[str] = Form(None),
    favorite_foods: Optional[str] = Form(None),
    least_preferred_foods: Optional[str] = Form(None),
    dietary_restrictions: Optional[str] = Form(None),
    meal_schedule: Optional[str] = Form(None),
    preferred_drinks: Optional[str] = Form(None),
    hydration_tracking: Optional[str] = Form(None),
    feeding_assistance_required: bool = Form(False),
    preferred_music_genre: Optional[str] = Form(None),
    favorite_color: Optional[str] = Form(None),
    least_preferred_color: Optional[str] = Form(None),
    preferred_smells: Optional[str] = Form(None),
    sensitivity_to_noise: bool = Form(False),
    sensitivity_to_light: bool = Form(False),
    favorite_activities: Optional[str] = Form(None),
    hobbies: Optional[str] = Form(None),
    former_profession: Optional[str] = Form(None),
    languages_spoken: Optional[str] = Form(None),
    religion_or_spiritual_beliefs: Optional[str] = Form(None),
    cultural_background: Optional[str] = Form(None),
    education_level: Optional[str] = Form(None),
    usual_sleep_time: Optional[str] = Form(None),
    wake_up_time: Optional[str] = Form(None),
    daily_routine_description: Optional[str] = Form(None),
    preferred_clothing_type: Optional[str] = Form(None),
    preferred_social_activity: Optional[str] = Form(None),
    wandering_tendency: bool = Form(False),
    incontinence_status: bool = Form(False),
    mobility_status: Optional[str] = Form(None),
    communication_method: Optional[str] = Form(None),
    agitation_triggers: Optional[str] = Form(None),
    calming_strategies: Optional[str] = Form(None),
    primary_caregiver_name: Optional[str] = Form(None),
    caregiver_relationship_to_patient: Optional[str] = Form(None),
    living_arrangement: Optional[str] = Form(None),
    social_support_services: Optional[str] = Form(None),
    blood_pressure: Optional[str] = Form(None),
    heart_rate: Optional[int] = Form(None),
    weight: Optional[float] = Form(None),
    height: Optional[float] = Form(None),
    blood_sugar_level: Optional[str] = Form(None),
    cholesterol_level: Optional[str] = Form(None),
) -> schemas.PatientCreate:
    return schemas.PatientCreate(**locals())

def image_file_handler(
    partner_image: UploadFile = File(None),
    children_image: UploadFile = File(None),
    pet_image: UploadFile = File(None),
    car_image: UploadFile = File(None),
    house_image: UploadFile = File(None),
) -> Dict[str, UploadFile]:
    return {
        "partner_image": partner_image,
        "children_image": children_image,
        "pet_image": pet_image,
        "car_image": car_image,
        "house_image": house_image,
    }
