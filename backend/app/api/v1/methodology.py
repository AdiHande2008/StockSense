from fastapi import APIRouter
from app.schemas.schemas import MethodologyResponse

router = APIRouter()

@router.get("/methodology", response_model=MethodologyResponse)
def get_methodology():
    return MethodologyResponse(
        project_goal="An educational, reproducible pipeline for predicting next-session Indian stock direction (UP or DOWN) using past-only daily data.",
        target_definition="Close-to-Close Direction: Target is 1 (UP) if next completed session's close > current session's close; 0 (DOWN) otherwise. Price ties are classified as DOWN.",
        supported_universe=[
            "RELIANCE (Reliance Industries)",
            "TCS (Tata Consultancy Services)",
            "INFY (Infosys)",
            "HDFCBANK (HDFC Bank)",
            "ICICIBANK (ICICI Bank)",
            "SBIN (State Bank of India)",
            "BHARTIARTL (Bharti Airtel)",
            "ITC (ITC Ltd.)",
            "LT (Larsen & Toubro)",
            "TATAMOTORS (Tata Motors)"
        ],
        features_contract=[
            "1-day return (pct change)",
            "2-day return (pct change)",
            "5-day return (pct change)",
            "SMA Ratio: (SMA_5 - SMA_20) / SMA_20",
            "5-day Rolling Volatility",
            "5-day Volume Ratio",
            "14-period RSI (Relative Strength Index)",
            "Day of Week (Monday=0 to Friday=4)"
        ],
        models_evaluated=[
            "Majority-Class Baseline (always predicts the most frequent class in training set)",
            "Logistic Regression (standardized features, L2 regularization)",
            "Random Forest Classifier (conservative depth=3 to prevent overfitting)"
        ],
        split_strategy="Strict chronological split: first 80% of historical dates for training, final 20% strictly untouched holdout test period. Zero shuffling or future lookahead leakage.",
        baseline_description="The Majority-Class Baseline predicts the most prevalent historical class without looking at technical indicators. A machine learning model is only meaningful if its balanced accuracy outperforms this simple baseline.",
        data_source_terms="EODHD end-of-day daily historical series for private student demonstration and educational learning. Not licensed for live trading or real-time redistribution.",
        disclaimer="EDUCATIONAL DEMONSTRATION ONLY. This system does not provide investment advice, buy/sell recommendations, target prices, or profit guarantees. Financial markets involve substantial risk."
    )
