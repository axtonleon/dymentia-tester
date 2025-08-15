# ai_services.py
import os
import io
import base64
from typing import List

# LangChain/Gemini for evaluation
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Free, lightweight TTS & STT
from gtts import gTTS
import assemblyai as aai

# Import schemas for type hinting and data structures
import schemas
from dotenv import load_dotenv
load_dotenv()

# --- INITIALIZATION ---

# Configure AssemblyAI client from environment variables
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# --- LANGCHAIN SETUP ---
parser = PydanticOutputParser(pydantic_object=schemas.Evaluation)

prompt_template = PromptTemplate(
    template="""You are an expert evaluator. Your task is to semantically compare a user's answer to a reference answer and provide a score and feedback.{format_instructions}Reference Answer: "{reference_answer}" User's Answer: "{user_answer}" """,
    input_variables=["reference_answer", "user_answer"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True
)

evaluation_chain = prompt_template | llm | parser

# --- SERVICE FUNCTIONS ---

def generate_question_audio(question_text: str) -> io.BytesIO:
    """
    Converts a string of text into an in-memory MP3 audio stream using gTTS.
    """
    tts = gTTS(text=question_text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def transcribe_audio_file(audio_file) -> str:
    """
    Transcribes an audio file object using AssemblyAI.
    Returns the transcribed text or an error message.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    if transcript.status == aai.TranscriptStatus.error:
        return f"[Transcription Error: {transcript.error}]"
    
    return transcript.text or "[No speech detected]"

def evaluate_answer(reference_answer: str, user_answer: str) -> schemas.Evaluation:
    """
    Uses the LangChain evaluation chain to compare the user's answer
    to the reference answer and returns a structured Evaluation object.
    """
    evaluation_result = evaluation_chain.invoke({
        "reference_answer": reference_answer,
        "user_answer": user_answer
    })
    return evaluation_result


def generate_quiz_summary(patient_name: str, results: List[schemas.QuizResultItem]) -> str:
    """Generates a personalized, high-level summary of the quiz session."""
    results_str = ""
    for item in results:
        results_str += f"- Question: {item.question_text}\n"
        results_str += f"  Answer: \"{item.transcribed_text}\"\n"
        results_str += f"  Score: {item.score}/100\n"

        # Handle response time safely - might be missing in older data
        response_time = getattr(item, 'response_time', 0.0)
        if response_time > 0:
            results_str += f"  Response Time: {response_time}s\n"
        results_str += "\n"

    summary_prompt = PromptTemplate.from_template(
        """
        You are a compassionate caregiver assistant. You are reviewing a memory quiz for a patient named {patient_name}.
        Based on the following results, write a brief, supportive, and encouraging summary for the primary caregiver.
        Focus on a high-level overview. Mention areas of strength and any potential areas of hesitation or struggle, but frame it gently.
        The goal is to provide insight, not a critical report.

        Consider both the accuracy of responses (scores) and response times when providing insights.
        Response times can indicate processing speed and cognitive fluency, but should be interpreted gently.
        Normal response times vary widely, so focus on patterns rather than individual times.

        Quiz Results for {patient_name}:
        {results}

        Summary:
        """
    )

    summary_chain = summary_prompt | llm
    summary_response = summary_chain.invoke({"patient_name": patient_name, "results": results_str})
    return summary_response.content