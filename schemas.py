from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

# --- API Request/Response Schemas ---

class TextToSpeechRequest(BaseModel):
    text: str

class EvaluationResult(BaseModel):
    transcribed_text: str
    response_time: float
    score: int
    feedback: str

class QuizQuestion(BaseModel):
    question_text: str
    reference_answer: str

# --- LangChain & Quiz Schemas ---

class Evaluation(BaseModel):
    """Pydantic model for structuring LLM evaluation output."""
    score: int = Field(description="Semantic accuracy score from 0 to 100.")
    feedback: str = Field(description="A brief explanation for the score.")

class QuizResultItem(BaseModel):
    """Represents a single item in the quiz results."""
    question_text: str
    transcribed_text: str
    score: int
    feedback: str

class QuizSummary(BaseModel):
    """Final quiz summary for the caregiver."""
    summary: str
    results: List[QuizResultItem]
    average_score: float

class QuizSummaryRequest(BaseModel):
    patient_id: int
    results: List[QuizResultItem]

# --- Patient Schemas ---

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    favorite_foods: Optional[str] = None
    least_preferred_foods: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    meal_schedule: Optional[str] = None
    preferred_drinks: Optional[str] = None
    hydration_tracking: Optional[str] = None
    feeding_assistance_required: bool = False
    preferred_music_genre: Optional[str] = None
    favorite_color: Optional[str] = None
    least_preferred_color: Optional[str] = None
    preferred_smells: Optional[str] = None
    sensitivity_to_noise: bool = False
    sensitivity_to_light: bool = False
    favorite_activities: Optional[str] = None
    hobbies: Optional[str] = None
    former_profession: Optional[str] = None
    languages_spoken: Optional[str] = None
    religion_or_spiritual_beliefs: Optional[str] = None
    cultural_background: Optional[str] = None
    education_level: Optional[str] = None
    usual_sleep_time: Optional[str] = None
    wake_up_time: Optional[str] = None
    daily_routine_description: Optional[str] = None
    preferred_clothing_type: Optional[str] = None
    preferred_social_activity: Optional[str] = None
    wandering_tendency: bool = False
    incontinence_status: bool = False
    mobility_status: Optional[str] = None
    communication_method: Optional[str] = None
    agitation_triggers: Optional[str] = None
    calming_strategies: Optional[str] = None
    primary_caregiver_name: Optional[str] = None
    caregiver_relationship_to_patient: Optional[str] = None
    living_arrangement: Optional[str] = None
    social_support_services: Optional[str] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    bmi: Optional[float] = None
    blood_sugar_level: Optional[str] = None
    cholesterol_level: Optional[str] = None

    class Config:
        orm_mode = True

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    partner_image_path: Optional[str] = None
    children_image_path: Optional[str] = None
    pet_image_path: Optional[str] = None
    car_image_path: Optional[str] = None
    house_image_path: Optional[str] = None
