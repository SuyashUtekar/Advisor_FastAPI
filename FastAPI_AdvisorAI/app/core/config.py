# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Life Insurance Advisor API"
    VERSION: str = "2.0"
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()
