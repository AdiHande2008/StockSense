from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from app.db.database import get_db
from app.models.entities import Instrument, DailyPrice
from app.schemas.schemas import InstrumentItem, InstrumentListResponse, PriceHistoryResponse, PricePoint

router = APIRouter()

@router.get("/instruments", response_model=InstrumentListResponse)
def list_instruments(
    exchange: Optional[str] = Query(None, description="Filter by exchange, e.g. NSE"),
    db: Session = Depends(get_db)
):
    query = db.query(Instrument).filter(Instrument.is_supported == True)
    if exchange:
        query = query.filter(Instrument.exchange == exchange.upper())
        
    instruments = query.order_by(Instrument.symbol).all()
    results = []
    
    for inst in instruments:
        latest_prices = (
            db.query(DailyPrice)
            .filter(DailyPrice.instrument_id == inst.id)
            .order_by(DailyPrice.trading_date.desc())
            .limit(2)
            .all()
        )
        
        latest_close = None
        change_pct = None
        latest_date = None
        
        if len(latest_prices) > 0:
            latest_close = round(latest_prices[0].close, 2)
            latest_date = latest_prices[0].trading_date
            if len(latest_prices) > 1 and latest_prices[1].close > 0:
                change = (latest_prices[0].close - latest_prices[1].close) / latest_prices[1].close
                change_pct = round(change * 100, 2)
                
        results.append(InstrumentItem(
            exchange=inst.exchange,
            symbol=inst.symbol,
            provider_symbol=inst.provider_symbol,
            display_name=inst.display_name,
            sector=inst.sector,
            currency=inst.currency,
            is_supported=inst.is_supported,
            latest_close=latest_close,
            change_pct=change_pct,
            latest_date=latest_date
        ))
        
    return InstrumentListResponse(items=results, total=len(results))

@router.get("/instruments/{exchange}/{symbol}", response_model=InstrumentItem)
def get_instrument_profile(exchange: str, symbol: str, db: Session = Depends(get_db)):
    inst = (
        db.query(Instrument)
        .filter(Instrument.exchange == exchange.upper(), Instrument.symbol == symbol.upper())
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instrument {exchange}:{symbol} not found")
        
    latest_prices = (
        db.query(DailyPrice)
        .filter(DailyPrice.instrument_id == inst.id)
        .order_by(DailyPrice.trading_date.desc())
        .limit(2)
        .all()
    )
    
    latest_close = None
    change_pct = None
    latest_date = None
    if len(latest_prices) > 0:
        latest_close = round(latest_prices[0].close, 2)
        latest_date = latest_prices[0].trading_date
        if len(latest_prices) > 1 and latest_prices[1].close > 0:
            change = (latest_prices[0].close - latest_prices[1].close) / latest_prices[1].close
            change_pct = round(change * 100, 2)
            
    return InstrumentItem(
        exchange=inst.exchange,
        symbol=inst.symbol,
        provider_symbol=inst.provider_symbol,
        display_name=inst.display_name,
        sector=inst.sector,
        currency=inst.currency,
        is_supported=inst.is_supported,
        latest_close=latest_close,
        change_pct=change_pct,
        latest_date=latest_date
    )

@router.get("/instruments/{exchange}/{symbol}/prices", response_model=PriceHistoryResponse)
def get_price_history(
    exchange: str,
    symbol: str,
    range: str = Query("1y", description="Time range: 1mo, 3mo, 6mo, 1y"),
    db: Session = Depends(get_db)
):
    inst = (
        db.query(Instrument)
        .filter(Instrument.exchange == exchange.upper(), Instrument.symbol == symbol.upper())
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instrument {exchange}:{symbol} not found")
        
    # Map range to days
    days_map = {
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365
    }
    days = days_map.get(range.lower(), 365)
    
    # Get latest date in db
    latest_row = (
        db.query(DailyPrice)
        .filter(DailyPrice.instrument_id == inst.id)
        .order_by(DailyPrice.trading_date.desc())
        .first()
    )
    if not latest_row:
        raise HTTPException(status_code=404, detail=f"No price data available for {symbol}")
        
    as_of = latest_row.trading_date
    from_date = as_of - timedelta(days=days)
    
    prices_query = (
        db.query(DailyPrice)
        .filter(DailyPrice.instrument_id == inst.id, DailyPrice.trading_date >= from_date)
        .order_by(DailyPrice.trading_date.asc())
        .all()
    )
    
    price_points = [
        PricePoint(
            date=p.trading_date,
            open=round(p.open, 2),
            high=round(p.high, 2),
            low=round(p.low, 2),
            close=round(p.close, 2),
            volume=p.volume
        )
        for p in prices_query
    ]
    
    return PriceHistoryResponse(
        exchange=inst.exchange,
        symbol=inst.symbol,
        display_name=inst.display_name,
        data_source="EODHD (Curated Daily Historical Series)",
        as_of_date=as_of,
        count=len(price_points),
        prices=price_points
    )
