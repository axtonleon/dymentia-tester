from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
import os

from database import init_db
from routes import router

app = FastAPI()


# Create uploads directory if it doesn't exist
os.makedirs("static/uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize the database
init_db()

app.include_router(router)
