from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class AdInDB(AdBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True