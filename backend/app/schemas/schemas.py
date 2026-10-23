from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    database_ready: bool
    model_count: int
    instruments_supported: int
    environment: str = "local-student"

class InstrumentItem(BaseModel):
    exchange: str
    symbol: str
    provider_symbol: str
    display_name: str
    sector: Optional[str] = None
    currency: str = "INR"
    is_supported: bool = True
    latest_close: Optional[float] = None
    change_pct: Optional[float] = None
    latest_date: Optional[date] = None

class InstrumentListResponse(BaseModel):
    items: List[InstrumentItem]
    total: int

class PricePoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class PriceHistoryResponse(BaseModel):
    exchange: str
    symbol: str
    display_name: str
    data_source: str
    as_of_date: date
    count: int
    prices: List[PricePoint]

class PredictionDetail(BaseModel):
    direction: str  # UP / DOWN
    as_of_date: date
    target_date: date
    data_cutoff_date: date
    stale: bool = False
    model_version: str
    model_label: str
    score: Optional[float] = None  # e.g. 0.58
    features_summary: Optional[Dict[str, Any]] = None

class EvaluationSummary(BaseModel):
    partition: str
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    samples: int
    accuracy: float
    balanced_accuracy: float
    baseline_balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: Optional[Dict[str, int]] = None

class LatestPredictionResponse(BaseModel):
    instrument: Dict[str, str]
    prediction: PredictionDetail
    evaluation: EvaluationSummary
    notice: str = "Educational model output only; not investment advice."

class WatchlistItemResponse(BaseModel):
    symbol: str
    exchange: str
    display_name: str
    sector: Optional[str] = None
    added_at: datetime

class WatchlistToggleRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"

class MethodologyResponse(BaseModel):
    project_goal: str
    target_definition: str
    supported_universe: List[str]
    features_contract: List[str]
    models_evaluated: List[str]
    split_strategy: str
    baseline_description: str
    data_source_terms: str
    disclaimer: str
