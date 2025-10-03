from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from .models import Trip
from .schemas import TripCreate, TripRead
from .auth import get_current_user
from .db import engine

router = APIRouter()

@router.post('/', response_model=TripRead)
def create_trip(trip: TripCreate, current_user=Depends(get_current_user)):
    dbtrip = Trip(**trip.dict(), user_id=current_user.id)
    if trip.start_date and trip.end_date:
        delta = trip.end_date - trip.start_date
        dbtrip.duration_minutes = int(delta.total_seconds() // 60)
    with Session(engine) as session:
        session.add(dbtrip)
        session.commit()
        session.refresh(dbtrip)
        return dbtrip

@router.get('/', response_model=List[TripRead])
def list_trips(current_user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(Trip).where(Trip.user_id == current_user.id)
        results = session.exec(statement).all()
        return results

@router.post('/sync')
def sync_trips(trips: List[TripCreate], current_user=Depends(get_current_user)):
    created = []
    with Session(engine) as session:
        for t in trips:
            dbtrip = Trip(**t.dict(), user_id=current_user.id, synced=True)
            if t.start_date and t.end_date:
                dbtrip.duration_minutes = int((t.end_date - t.start_date).total_seconds() // 60)
            session.add(dbtrip)
            session.commit()
            session.refresh(dbtrip)
            created.append(dbtrip)
    return {'created': len(created)}
