from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class PriceBase(BaseModel):
    crop_name: str
    variety: Optional[str] = None
    grade: Optional[str] = None
    district: str
    mandi_name: str
    arrival: Optional[float] = None
    unit: Optional[str] = None
    price_per_quintal: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_date: date
    last_updated: Optional[datetime] = None


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    grade: Optional[str] = None
    district: Optional[str] = None
    mandi_name: Optional[str] = None
    arrival: Optional[float] = None
    unit: Optional[str] = None
    price_per_quintal: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_date: Optional[date] = None
    last_updated: Optional[datetime] = None


class PriceInDB(PriceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
