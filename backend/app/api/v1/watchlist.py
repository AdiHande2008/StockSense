from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.entities import Instrument, WatchlistItem
from app.schemas.schemas import WatchlistItemResponse, WatchlistToggleRequest

router = APIRouter()

@router.get("/watchlist", response_model=List[WatchlistItemResponse])
def get_watchlist(user_id: str = "demo-user", db: Session = Depends(get_db)):
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id)
        .join(Instrument)
        .all()
    )
    results = []
    for w in items:
        inst = w.instrument
        results.append(WatchlistItemResponse(
            symbol=inst.symbol,
            exchange=inst.exchange,
            display_name=inst.display_name,
            sector=inst.sector,
            added_at=w.created_at
        ))
    return results

@router.post("/watchlist", response_model=WatchlistItemResponse)
def toggle_watchlist_item(req: WatchlistToggleRequest, user_id: str = "demo-user", db: Session = Depends(get_db)):
    inst = (
        db.query(Instrument)
        .filter(Instrument.exchange == req.exchange.upper(), Instrument.symbol == req.symbol.upper())
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail=f"Instrument {req.symbol} not found")
        
    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id, WatchlistItem.instrument_id == inst.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return WatchlistItemResponse(
            symbol=inst.symbol,
            exchange=inst.exchange,
            display_name=inst.display_name,
            sector=inst.sector,
            added_at=existing.created_at
        )
    else:
        new_item = WatchlistItem(user_id=user_id, instrument_id=inst.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return WatchlistItemResponse(
            symbol=inst.symbol,
            exchange=inst.exchange,
            display_name=inst.display_name,
            sector=inst.sector,
            added_at=new_item.created_at
        )

@router.delete("/watchlist/{exchange}/{symbol}", status_code=204)
def remove_watchlist_item(exchange: str, symbol: str, user_id: str = "demo-user", db: Session = Depends(get_db)):
    inst = (
        db.query(Instrument)
        .filter(Instrument.exchange == exchange.upper(), Instrument.symbol == symbol.upper())
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
        
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id, WatchlistItem.instrument_id == inst.id)
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return None
