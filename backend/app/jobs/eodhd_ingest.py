import os
import requests
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.db.database import SessionLocal
from app.models.entities import Instrument, DailyPrice
from app.core.config import settings

EODHD_BASE_URL = "https://eodhistoricaldata.com/api/eod"

def fetch_eodhd_prices(provider_symbol: str, api_key: str, from_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches daily OHLCV from EODHD for a given symbol (e.g. RELIANCE.NSE).
    Free tier allows 20 calls/day and 1 year of daily history.
    """
    params = {
        "api_token": api_key,
        "fmt": "json",
        "order": "a"  # ascending
    }
    if from_date:
        params["from"] = from_date
        
    url = f"{EODHD_BASE_URL}/{provider_symbol}"
    response = requests.get(url, params=params, timeout=15)
    if response.status_code == 403 or response.status_code == 401:
        raise PermissionError(f"EODHD API authentication failed: {response.text}")
    elif response.status_code != 200:
        raise RuntimeError(f"EODHD API returned status {response.status_code}: {response.text}")
        
    data = response.json()
    if not isinstance(data, list):
        raise ValueError(f"Unexpected response format from EODHD: {data}")
    return data

def ingest_symbol(symbol: str, api_key: Optional[str] = None):
    key = api_key or settings.EODHD_API_KEY
    if not key or key == "demo_key":
        print(f"[INFO] No valid EODHD_API_KEY provided. Keeping local curated dataset for {symbol}.")
        return {"status": "skipped", "reason": "No API key configured. Curated dataset active."}
        
    db = SessionLocal()
    try:
        inst = db.query(Instrument).filter_by(symbol=symbol).first()
        if not inst:
            print(f"[ERROR] Instrument {symbol} not found in database.")
            return {"status": "error", "reason": f"Instrument {symbol} not registered."}
            
        print(f"Fetching live EODHD data for {inst.provider_symbol}...")
        raw_data = fetch_eodhd_prices(inst.provider_symbol, api_key=key)
        
        inserted = 0
        for row in raw_data:
            t_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            adj_c = float(row.get("adjusted_close", c))
            v = int(row.get("volume", 0))
            
            # Validation: OHLC sanity checks
            if h < l or o <= 0 or c <= 0 or v < 0:
                continue
                
            existing = db.query(DailyPrice).filter_by(instrument_id=inst.id, trading_date=t_date).first()
            if not existing:
                dp = DailyPrice(
                    instrument_id=inst.id,
                    trading_date=t_date,
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    adjusted_close=adj_c,
                    volume=v,
                    data_source="EODHD Live API",
                    ingested_at=datetime.utcnow()
                )
                db.add(dp)
                inserted += 1
        db.commit()
        print(f"[SUCCESS] Ingestion for {symbol} complete. {inserted} new records added.")
        return {"status": "success", "new_records": inserted}
    except Exception as e:
        db.rollback()
        print(f"[WARN] Error ingesting {symbol}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE"
    ingest_symbol(target)
