from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # AI provider configuration
    PROVIDER: str = "google_cloud_vision"
    MIN_CONFIDENCE: float = 0.7
    MAX_TAGS_PER_POST: int = 5
    GOOGLE_VISION_API_KEY: str = os.getenv("GOOGLE_VISION_API_KEY")

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Security settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    

@lru_cache()
def get_settings():
    return Settings()