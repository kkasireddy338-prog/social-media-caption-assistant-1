import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/caption_assistant.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
