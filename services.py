from sqlalchemy.orm import Session
import models, schemas

def create_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(
        image_path=question.image_path,
        question=question.question,
        answer=question.answer
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Question).offset(skip).limit(limit).all()

def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

def get_questions_count(db: Session):
    count = db.query(models.Question).count()
    return count if count is not None else 0

def update_question(db: Session, question_id: int, question_data: schemas.QuestionUpdate):
    db_question = get_question(db, question_id)
    if db_question:
        db_question.question = question_data.question
        db_question.answer = question_data.answer
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int):
    db_question = get_question(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
    return db_question