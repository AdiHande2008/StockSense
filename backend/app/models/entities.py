import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, BigInteger, Boolean, Date, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Instrument(Base):
    __tablename__ = "instruments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    exchange = Column(String(10), nullable=False, default="NSE")
    symbol = Column(String(30), nullable=False, index=True)
    provider_symbol = Column(String(50), nullable=False)
    display_name = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=False, default="INR")
    is_supported = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("exchange", "symbol", name="uq_exchange_symbol"),)
    
    prices = relationship("DailyPrice", back_populates="instrument", cascade="all, delete-orphan")
    models = relationship("ModelVersion", back_populates="instrument", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="instrument", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="instrument", cascade="all, delete-orphan")


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(String, ForeignKey("instruments.id"), nullable=False, index=True)
    trading_date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    data_source = Column(String(100), default="EODHD (Curated Starter Dataset)")
    ingested_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("instrument_id", "trading_date", name="uq_instrument_date"),)
    instrument = relationship("Instrument", back_populates="prices")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instrument_id = Column(String, ForeignKey("instruments.id"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)  # MAJORITY_BASELINE, LOGISTIC_REGRESSION, RANDOM_FOREST
    status = Column(String(20), default="PUBLISHED") # PUBLISHED, CANDIDATE, RETIRED
    artifact_path = Column(String(255), nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    
    instrument = relationship("Instrument", back_populates="models")
    metrics = relationship("EvaluationMetric", back_populates="model_version", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="model_version", cascade="all, delete-orphan")


class EvaluationMetric(Base):
    __tablename__ = "evaluation_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False, index=True)
    partition = Column(String(20), nullable=False)  # TRAIN, VALIDATION, TEST
    accuracy = Column(Float, nullable=False)
    balanced_accuracy = Column(Float, nullable=False)
    baseline_balanced_accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1 = Column(Float, nullable=False)
    samples = Column(Integer, nullable=False)
    confusion_matrix_json = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model_version = relationship("ModelVersion", back_populates="metrics")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instrument_id = Column(String, ForeignKey("instruments.id"), nullable=False, index=True)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    direction = Column(String(10), nullable=False)  # UP, DOWN
    score = Column(Float, nullable=True)  # Calibrated probability (e.g. 0.58)
    features_summary_json = Column(Text, nullable=True)
    stale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    instrument = relationship("Instrument", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, default="demo-user", index=True)
    instrument_id = Column(String, ForeignKey("instruments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("user_id", "instrument_id", name="uq_user_instrument"),)
    instrument = relationship("Instrument", back_populates="watchlist_items")
