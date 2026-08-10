from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdminCreate(BaseModel):
    name: str
    email: str
    password: str

class AdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_approved: Optional[bool] = None
    profile_photo: Optional[str] = None

class AdminInDB(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_approved: bool
    profile_photo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
