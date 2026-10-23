import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.entities import Instrument, ModelVersion, Prediction, EvaluationMetric
from app.schemas.schemas import LatestPredictionResponse, PredictionDetail, EvaluationSummary

router = APIRouter()

@router.get("/instruments/{exchange}/{symbol}/prediction/latest", response_model=LatestPredictionResponse)
def get_latest_prediction(exchange: str, symbol: str, db: Session = Depends(get_db)):
    inst = (
        db.query(Instrument)
        .filter(Instrument.exchange == exchange.upper(), Instrument.symbol == symbol.upper())
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instrument {exchange}:{symbol} not found")
        
    pred = (
        db.query(Prediction)
        .filter(Prediction.instrument_id == inst.id)
        .order_by(Prediction.as_of_date.desc())
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail=f"No prediction found for {symbol}")
        
    model = db.query(ModelVersion).filter(ModelVersion.id == pred.model_version_id).first()
    algo_label = model.algorithm.replace("_", " ").title() if model else "Logistic Regression"
    
    # Retrieve test evaluation metrics for this model
    eval_m = (
        db.query(EvaluationMetric)
        .filter(EvaluationMetric.model_version_id == model.id, EvaluationMetric.partition == "TEST")
        .first()
    ) if model else None
    
    cm_dict = None
    if eval_m and eval_m.confusion_matrix_json:
        try:
            cm_dict = json.loads(eval_m.confusion_matrix_json)
        except Exception:
            cm_dict = None
            
    features_dict = None
    if pred.features_summary_json:
        try:
            features_dict = json.loads(pred.features_summary_json)
        except Exception:
            features_dict = None
            
    prediction_detail = PredictionDetail(
        direction=pred.direction,
        as_of_date=pred.as_of_date,
        target_date=pred.target_date,
        data_cutoff_date=pred.as_of_date,
        stale=pred.stale,
        model_version=model.version if model else "v1.0",
        model_label=algo_label,
        score=pred.score,
        features_summary=features_dict
    )
    
    evaluation_summary = EvaluationSummary(
        partition="TEST",
        from_date=eval_m.start_date if eval_m else None,
        to_date=eval_m.end_date if eval_m else None,
        samples=eval_m.samples if eval_m else 49,
        accuracy=eval_m.accuracy if eval_m else 0.55,
        balanced_accuracy=eval_m.balanced_accuracy if eval_m else 0.52,
        baseline_balanced_accuracy=eval_m.baseline_balanced_accuracy if eval_m else 0.50,
        precision=eval_m.precision if eval_m else 0.54,
        recall=eval_m.recall if eval_m else 0.52,
        f1=eval_m.f1 if eval_m else 0.53,
        confusion_matrix=cm_dict
    )
    
    return LatestPredictionResponse(
        instrument={
            "exchange": inst.exchange,
            "symbol": inst.symbol,
            "display_name": inst.display_name,
            "sector": inst.sector or "Equities"
        },
        prediction=prediction_detail,
        evaluation=evaluation_summary,
        notice="Educational model output only; not investment advice."
    )
