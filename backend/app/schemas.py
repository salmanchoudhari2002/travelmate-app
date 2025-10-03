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
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    destination: Optional[str] = None
    mode: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    expenses: Optional[float] = 0.0
    purpose: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail: Optional[str] = None

class TripRead(TripCreate):
    id: int
    user_id: int
    duration_minutes: Optional[int]
    synced: bool
    created_at: datetime
    image_url: Optional[str] = None
    thumbnail: Optional[str] = None

    class Config:
        orm_mode = True
