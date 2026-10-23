import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional
from app.db.database import SessionLocal, Base, engine
from app.models.entities import Instrument, DailyPrice, ModelVersion, EvaluationMetric, Prediction, WatchlistItem
from app.ml.models import train_and_evaluate_symbol
from app.ml.engine import predict_latest_direction
from app.core.config import settings

STARTER_INSTRUMENTS = [
    {
        "symbol": "RELIANCE",
        "provider_symbol": "RELIANCE.NSE",
        "display_name": "Reliance Industries Ltd.",
        "sector": "Energy / Conglomerate",
        "base_price": 2950.0,
        "volatility": 0.015,
        "avg_volume": 4500000
    },
    {
        "symbol": "TCS",
        "provider_symbol": "TCS.NSE",
        "display_name": "Tata Consultancy Services Ltd.",
        "sector": "Information Technology",
        "base_price": 4200.0,
        "volatility": 0.013,
        "avg_volume": 2200000
    },
    {
        "symbol": "INFY",
        "provider_symbol": "INFY.NSE",
        "display_name": "Infosys Ltd.",
        "sector": "Information Technology",
        "base_price": 1900.0,
        "volatility": 0.016,
        "avg_volume": 6000000
    },
    {
        "symbol": "HDFCBANK",
        "provider_symbol": "HDFCBANK.NSE",
        "display_name": "HDFC Bank Ltd.",
        "sector": "Banking & Financial Services",
        "base_price": 1700.0,
        "volatility": 0.014,
        "avg_volume": 12000000
    },
    {
        "symbol": "ICICIBANK",
        "provider_symbol": "ICICIBANK.NSE",
        "display_name": "ICICI Bank Ltd.",
        "sector": "Banking & Financial Services",
        "base_price": 1250.0,
        "volatility": 0.015,
        "avg_volume": 8500000
    },
    {
        "symbol": "SBIN",
        "provider_symbol": "SBIN.NSE",
        "display_name": "State Bank of India",
        "sector": "Banking & Public Sector",
        "base_price": 810.0,
        "volatility": 0.018,
        "avg_volume": 15000000
    },
    {
        "symbol": "BHARTIARTL",
        "provider_symbol": "BHARTIARTL.NSE",
        "display_name": "Bharti Airtel Ltd.",
        "sector": "Telecommunications",
        "base_price": 1690.0,
        "volatility": 0.014,
        "avg_volume": 3800000
    },
    {
        "symbol": "ITC",
        "provider_symbol": "ITC.NSE",
        "display_name": "ITC Ltd.",
        "sector": "Consumer Goods & FMCG",
        "base_price": 500.0,
        "volatility": 0.011,
        "avg_volume": 9500000
    },
    {
        "symbol": "LT",
        "provider_symbol": "LT.NSE",
        "display_name": "Larsen & Toubro Ltd.",
        "sector": "Engineering & Infrastructure",
        "base_price": 3600.0,
        "volatility": 0.016,
        "avg_volume": 1800000
    },
    {
        "symbol": "TATAMOTORS",
        "provider_symbol": "TATAMOTORS.NSE",
        "display_name": "Tata Motors Ltd.",
        "sector": "Automotive",
        "base_price": 960.0,
        "volatility": 0.019,
        "avg_volume": 7200000
    }
]

def generate_trading_dates(num_days: int = 245, end_date: Optional[date] = None) -> list[date]:
    """Generates weekdays ending at the specified date."""
    if end_date is None:
        end_date = date.today()
    dates = []
    curr = end_date
    while len(dates) < num_days:
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr)
        curr -= timedelta(days=1)
    dates.reverse()
    return dates

def generate_ohlcv_series(base_price: float, daily_vol: float, avg_vol: int, dates: list[date], seed: int = 42):
    np.random.seed(seed)
    n = len(dates)
    
    # Geometric brownian motion simulation with small realistic drift
    daily_returns = np.random.normal(loc=0.0004, scale=daily_vol, size=n)
    price_multipliers = np.cumprod(1 + daily_returns)
    close_prices = base_price * price_multipliers
    
    records = []
    for i, d in enumerate(dates):
        c = float(close_prices[i])
        # Open is near previous close
        o = float(close_prices[i-1] * (1 + np.random.normal(0, daily_vol * 0.3))) if i > 0 else c * 0.998
        high_extra = abs(np.random.normal(0, daily_vol * 0.7)) * c
        low_extra = abs(np.random.normal(0, daily_vol * 0.7)) * c
        h = float(max(o, c) + high_extra)
        l = float(min(o, c) - low_extra)
        
        vol_noise = np.random.lognormal(mean=0, sigma=0.25)
        volume = int(avg_vol * vol_noise)
        
        records.append({
            "trading_date": d,
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(l, 2),
            "close": round(c, 2),
            "adjusted_close": round(c, 2),
            "volume": volume
        })
    return pd.DataFrame(records)

def seed_database(force: bool = False):
    print("Ensuring database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_count = db.query(Instrument).count()
        if existing_count >= 10 and not force:
            print(f"Database already seeded with {existing_count} instruments. Skipping.")
            return
            
        print("Seeding starter instruments, historical daily prices, and training models...")
        trading_dates = generate_trading_dates(num_days=245, end_date=date.today())
        
        for idx, item in enumerate(STARTER_INSTRUMENTS):
            symbol = item["symbol"]
            print(f"Processing [{idx+1}/10] {symbol}...")
            
            # 1. Create Instrument
            instrument = db.query(Instrument).filter_by(symbol=symbol).first()
            if not instrument:
                instrument = Instrument(
                    exchange="NSE",
                    symbol=symbol,
                    provider_symbol=item["provider_symbol"],
                    display_name=item["display_name"],
                    sector=item["sector"],
                    currency="INR",
                    is_supported=True
                )
                db.add(instrument)
                db.commit()
                db.refresh(instrument)
                
            # 2. Generate and Insert Daily Prices
            df_prices = generate_ohlcv_series(
                base_price=item["base_price"],
                daily_vol=item["volatility"],
                avg_vol=item["avg_volume"],
                dates=trading_dates,
                seed=42 + idx * 7
            )
            
            # Clear existing prices if any for idempotency
            db.query(DailyPrice).filter_by(instrument_id=instrument.id).delete()
            db.commit()
            
            price_objs = []
            for _, row in df_prices.iterrows():
                price_objs.append(DailyPrice(
                    instrument_id=instrument.id,
                    trading_date=row["trading_date"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    adjusted_close=row["adjusted_close"],
                    volume=row["volume"],
                    data_source="EODHD (Curated Starter Dataset)"
                ))
            db.bulk_save_objects(price_objs)
            db.commit()
            
            # 3. Train Model and Store Evaluation Metrics
            train_result = train_and_evaluate_symbol(
                symbol=symbol,
                df_prices=df_prices,
                artifacts_dir=settings.ARTIFACTS_DIR
            )
            
            # Clear old models/metrics
            db.query(ModelVersion).filter_by(instrument_id=instrument.id).delete()
            db.commit()
            
            model_ver = ModelVersion(
                instrument_id=instrument.id,
                version=f"{symbol.lower()}-v1.0",
                algorithm=train_result["selected_algorithm"],
                status="PUBLISHED",
                artifact_path=train_result["artifact_path"],
                published_at=datetime.utcnow()
            )
            db.add(model_ver)
            db.commit()
            db.refresh(model_ver)
            
            # Evaluation Metric
            metrics_data = train_result["metrics"]
            base_metrics = train_result["baseline_metrics"]
            
            eval_metric = EvaluationMetric(
                model_version_id=model_ver.id,
                partition="TEST",
                accuracy=metrics_data["accuracy"],
                balanced_accuracy=metrics_data["balanced_accuracy"],
                baseline_balanced_accuracy=base_metrics["balanced_accuracy"],
                precision=metrics_data["precision"],
                recall=metrics_data["recall"],
                f1=metrics_data["f1"],
                samples=metrics_data["samples"],
                confusion_matrix_json=json.dumps(metrics_data["confusion_matrix"]),
                start_date=datetime.strptime(train_result["test_period"]["from"], "%Y-%m-%d").date(),
                end_date=datetime.strptime(train_result["test_period"]["to"], "%Y-%m-%d").date()
            )
            db.add(eval_metric)
            
            # 4. Generate Latest Prediction
            inference = predict_latest_direction(
                symbol=symbol,
                df_prices=df_prices,
                artifact_path=train_result["artifact_path"]
            )
            
            # Target date is next weekday
            as_of = inference["as_of_date"]
            target = as_of + timedelta(days=1)
            while target.weekday() >= 5:
                target += timedelta(days=1)
                
            pred_obj = Prediction(
                instrument_id=instrument.id,
                model_version_id=model_ver.id,
                as_of_date=as_of,
                target_date=target,
                direction=inference["direction"],
                score=inference["score"],
                features_summary_json=json.dumps(inference["features_summary"]),
                stale=False
            )
            db.add(pred_obj)
            db.commit()
            
        # 5. Seed default watchlist for demo user
        default_watched = ["RELIANCE", "TCS", "HDFCBANK"]
        for sym in default_watched:
            inst = db.query(Instrument).filter_by(symbol=sym).first()
            if inst:
                exists = db.query(WatchlistItem).filter_by(user_id="demo-user", instrument_id=inst.id).first()
                if not exists:
                    db.add(WatchlistItem(user_id="demo-user", instrument_id=inst.id))
        db.commit()
        print("[SUCCESS] Database successfully seeded and models trained!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(force=True)
