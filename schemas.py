from pydantic import BaseModel, Field
from typing import List

class QuestionBase(BaseModel):
    image_path: str
    question: str
    answer: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True

class QuestionUpdate(BaseModel):
    question: str
    answer: str

class TextToSpeechRequest(BaseModel):
    text: str

class Evaluation(BaseModel):
    score: int = Field(..., description="The score from 0 to 100.")
    feedback: str = Field(..., description="Constructive feedback for the user.")

class EvaluationResult(BaseModel):
    transcribed_text: str
    response_time: float
    score: int
    feedback: str
    reference_answer: str

class QuizResultItem(BaseModel):
    question_text: str
    transcribed_text: str
    score: int
    response_time: float = 0.0  # Default to 0.0 for backward compatibility
    reference_answer: str

class QuizSummaryRequest(BaseModel):
    results: List[QuizResultItem]

class QuizSummary(BaseModel):
    summary: str
    results: List[QuizResultItem]
    average_score: float
    average_response_time: float