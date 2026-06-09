from typing import List, Optional  # Import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "AI Weather Care"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Changing this back to Optional[str] = None prevents the boot crash
    # BROWSERLESS_API_KEY: Optional[str] = None 
    BROWSERLESS_API_KEY: str = "2UfnLXfi1MJzAhS0c95b67cdee45fd1e5225f533d38cee9c4" 
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

settings = Settings()