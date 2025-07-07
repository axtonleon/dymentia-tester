# main.py
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

import models, routes
from database import engine

# --- INITIALIZATION ---
load_dotenv()

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Information and Quiz API")

# --- JINJA2 SETUP ---
def json_script(value, element_id):
    json_string = json.dumps(value)
    return Markup(f'<script id="{element_id}" type="application/json">{json_string}</script>')

# This is a bit of a workaround to get the templates object from routes.py
# In a larger application, you might use a shared dependency injection system.
routes.templates.env.filters['json_script'] = json_script

# Mount the static directory to serve CSS, JS, and uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routes from routes.py
app.include_router(routes.router)