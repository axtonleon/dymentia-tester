from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

    def __repr__(self):
        return f'<Question {self.question}>'