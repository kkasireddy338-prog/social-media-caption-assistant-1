import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # On Vercel / serverless environments, root filesystem is read-only, so SQLite MUST be in /tmp
    if os.environ.get('VERCEL'):
        DATABASE_PATH = '/tmp/caption_assistant.db'
    else:
        DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/caption_assistant.db')
        
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False

