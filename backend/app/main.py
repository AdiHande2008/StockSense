from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base
from app.jobs.seed_data import seed_database
from app.api.v1 import health, instruments, predictions, methodology, watchlist

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Educational Indian Equity Direction (UP/DOWN) Prediction & Evaluation API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(instruments.router, prefix=settings.API_V1_STR, tags=["Instruments"])
app.include_router(predictions.router, prefix=settings.API_V1_STR, tags=["Predictions"])
app.include_router(methodology.router, prefix=settings.API_V1_STR, tags=["Methodology"])
app.include_router(watchlist.router, prefix=settings.API_V1_STR, tags=["Watchlist"])

# Also mount under /api for convenient frontend access
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(instruments.router, prefix="/api", tags=["Instruments"])
app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(methodology.router, prefix="/api", tags=["Methodology"])
app.include_router(watchlist.router, prefix="/api", tags=["Watchlist"])

@app.on_event("startup")
def on_startup():
    # Automatically seed the database and train starter models on first run
    seed_database(force=False)

@app.get("/")
def root():
    return {
        "project": "StockSense AI",
        "description": "Educational Indian Equity Direction Prediction Engine",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
