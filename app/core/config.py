from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Devin's Nest API 接口文档"
    API_V1_STR: str = "/api/v1"
    
    # 对外可访问的基础地址（含协议与端口），用于拼接上传文件等返回 URL。
    # 反向代理/Cloudflare 会让 request.base_url 丢失端口（如 :8443），导致返回的
    # URL 落到 443 上而无法访问。留空则回退到 request.base_url（本地开发用）。
    # 线上 .env 设置：PUBLIC_BASE_URL=https://devinnest-api.top:8443
    PUBLIC_BASE_URL: str = ""

    # LLM Configuration (Placeholder for actual keys)
    OPENAI_API_KEY: str = ""
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost", 
        "http://localhost:3000", 
        "http://localhost:4321",
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
