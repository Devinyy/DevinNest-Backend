from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Devin's Nest API 接口文档"
    API_V1_STR: str = "/api/v1"
    
    # LLM Configuration (Placeholder for actual keys)
    OPENAI_API_KEY: str = ""
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "https://devinnest.top",
        "https://www.devinnest.top",
        "https://www.devinneststage.top",
        "https://devinneststage.top",
        "https://devinnest-api.top",
        "https://devinnest-api.top:8443"
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
