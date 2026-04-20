import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret")
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = "../.env"

settings = Settings()
