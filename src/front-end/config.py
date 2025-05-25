import os
from dotenv import load_dotenv
import urllib.parse
from typing import List, Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

# Define Settings class for frontend
class Settings:
    def __init__(self):
        # Frontend settings
        self.BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.PORT = int(os.getenv("FRONTEND_PORT", "5001"))
        self.HOST = os.getenv("FRONTEND_HOST", "0.0.0.0")
        self.DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
        
        # Upload settings
        self.FILE_DEFAULT_CHUNK_SIZE = int(os.getenv("FILE_DEFAULT_CHUNK_SIZE", "512000"))
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
        
        # Document types
        self.ALLOWED_FILE_TYPES = ["text/plain", "application/pdf", "application/msword", 
                                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Get settings function
def get_settings() -> Settings:
    """Returns the settings instance"""
    return Settings()

# Database configuration - Using SQLite for simplicity
USE_SQLITE = True  # Set to True to use SQLite, False to use PostgreSQL

if USE_SQLITE:
    # SQLite configuration - easier for development
    # Put database in a dedicated data directory inside src/front-end
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    # Create the data directory if it doesn't exist
    if not os.path.exists(data_dir):
        print(f"Creating data directory at: {data_dir}")
        os.makedirs(data_dir)
    
    # Use a more appropriate path for the SQLite database
    db_path = os.path.join(data_dir, "sqlite.db")
    print(f"Using SQLite for database at: {db_path}")
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    # PostgreSQL configuration - using values from DBeaver connection
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")  # Replace with your actual password
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")  # Using 'postgres' as database name from screenshot

    # Debug info
    print(f"Using PostgreSQL for database")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    
    # Construct database URL with URL-encoded password
    # This is important if the password contains special characters
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
    DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Web server configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5001'))

# JWT configuration
SECRET_KEY = os.getenv('SECRET_KEY', '9231c9496752f3887965250eeda37e544232680d0b23a760b8caa8d9112d9618')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Backend API configuration
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@minirag.com')
VERIFICATION_TOKEN_EXPIRY_HOURS = int(os.getenv('VERIFICATION_TOKEN_EXPIRY_HOURS', '24'))

# Base URL for application
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001') 