from sqlalchemy import Column, Integer, String, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    image_data = Column(LargeBinary, nullable=False)  # Store binary image data
    image_filename = Column(String, nullable=False)   # Store original filename for content-type
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

    def __repr__(self):
        return f'<Question {self.question}>'