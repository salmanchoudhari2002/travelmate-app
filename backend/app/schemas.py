from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TripCreate(BaseModel):
    start_lat: Optional[float]
    start_lng: Optional[float]
    destination: Optional[str]
    mode: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    expenses: Optional[float] = 0.0
    purpose: Optional[str]
    notes: Optional[str]

class TripRead(TripCreate):
    id: int
    user_id: int
    duration_minutes: Optional[int]
    synced: bool
    created_at: datetime

    class Config:
        orm_mode = True
