import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "StockSense AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite default for zero-friction local run; seamless switch to postgresql if provided
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stocksense.db")
    
    # EODHD API Key (Optional: seed data is pre-bundled for local offline learning)
    EODHD_API_KEY: str = os.getenv("EODHD_API_KEY", "")
    
    # Storage directory for trained scikit-learn models
    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts"))
    
    # CORS origins allowing local Next.js frontend
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = Settings()
