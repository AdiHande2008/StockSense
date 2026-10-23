from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.entities import Instrument, ModelVersion
from app.schemas.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    try:
        inst_count = db.query(Instrument).count()
        model_count = db.query(ModelVersion).count()
        db_ready = True
    except Exception:
        inst_count = 0
        model_count = 0
        db_ready = False
        
    return HealthResponse(
        status="healthy" if db_ready else "degraded",
        version=settings.VERSION,
        database_ready=db_ready,
        model_count=model_count,
        instruments_supported=inst_count,
        environment="local-student"
    )
