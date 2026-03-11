import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management & CSRF protection
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")

    # Database configuration (default: SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'app.db')}"

    # Disable modification tracking (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, "static", "img")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
