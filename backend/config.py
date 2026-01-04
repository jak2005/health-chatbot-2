# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SONAR_API_KEY = os.getenv('SONAR_API_KEY')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    # Database Configuration
    CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chromadb')
    
    # Model Configuration
    GEMINI_FLASH_MODEL = "gemini-1.5-flash"
    GEMINI_PRO_MODEL = "gemini-1.5-pro"
    SONAR_MODEL = "llama-3.1-sonar-small-128k-online"
    
    # Chat Configuration
    MAX_CHAT_HISTORY = 10
    MAX_SUB_QUERIES = 4
    
    # Response Configuration
    DEFAULT_RESPONSE = "I apologize, but I'm having trouble processing your request. Please try again."
    SAFETY_WARNING = "For your safety, please consult a healthcare professional for accurate advice."
    
    # Session Configuration
    STREAMLIT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    # WhatsApp Configuration
    WHATSAPP_ENABLED = bool(os.getenv('TWILIO_ACCOUNT_SID') and 
                           os.getenv('TWILIO_AUTH_TOKEN') and 
                           os.getenv('TWILIO_WHATSAPP_NUMBER'))
