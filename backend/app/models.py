from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    start_lat: Optional[float]
    start_lng: Optional[float]
    destination: Optional[str]
    mode: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    duration_minutes: Optional[int]
    expenses: Optional[float] = 0.0
    purpose: Optional[str]
    notes: Optional[str]
    synced: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
