from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "AI Weather Care"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    # Google Forms
    # GOOGLE_FORM_BASE_URL: str = "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform?usp=pp_url&entry.1234567={}&entry.9876543={}"

settings = Settings()
