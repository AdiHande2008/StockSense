import os
import joblib
import pandas as pd
from typing import Dict, Any, Optional
from app.ml.features import FEATURE_COLUMNS, extract_features

def predict_latest_direction(symbol: str, df_prices: pd.DataFrame, artifact_path: str) -> Dict[str, Any]:
    """
    Computes features as of the latest trading session and predicts
    direction for the upcoming session.
    """
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Model artifact not found for {symbol} at {artifact_path}")
        
    model = joblib.load(artifact_path)
    
    # Extract features for all rows up to latest
    df_features = extract_features(df_prices, include_target=False)
    if len(df_features) == 0:
        raise ValueError(f"Not enough price history to compute features for {symbol}")
        
    latest_row = df_features.iloc[-1]
    X_latest = latest_row[FEATURE_COLUMNS].to_frame().T
    
    # Predict direction and probability
    pred_class = int(model.predict(X_latest)[0])
    direction = "UP" if pred_class == 1 else "DOWN"
    
    score = None
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_latest)[0]
        # probability of the predicted direction
        score = float(probs[pred_class])
        
    # Technical feature snapshot
    features_summary = {
        "return_1d_pct": round(float(latest_row["return_1d"]) * 100, 2),
        "return_5d_pct": round(float(latest_row["return_5d"]) * 100, 2),
        "rsi_14": round(float(latest_row["rsi_14"]), 1),
        "sma_ratio_pct": round(float(latest_row["sma_ratio"]) * 100, 2),
        "volatility_5d_pct": round(float(latest_row["volatility_5d"]) * 100, 2),
        "volume_ratio_5d": round(float(latest_row["volume_ratio_5d"]), 2),
        "macd_hist": round(float(latest_row.get("macd_hist", 0.0)), 4),
        "bollinger_b": round(float(latest_row.get("bollinger_b", 0.5)), 2),
    }
    
    return {
        "direction": direction,
        "score": round(score, 2) if score is not None else 0.50,
        "as_of_date": latest_row["trading_date"],
        "features_summary": features_summary
    }
