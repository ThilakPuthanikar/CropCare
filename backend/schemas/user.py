from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    phone_number: Optional[str] = None
    district: Optional[str] = None
    land_size: Optional[float] = None
    irrigation_type: Optional[str] = None
    profile_photo: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    is_approved: Optional[bool] = None
    district: Optional[str] = None
    land_size: Optional[float] = None
    irrigation_type: Optional[str] = None
    profile_photo: Optional[str] = None

class UserInDB(UserBase):
    id: int
    role: str
    is_approved: bool
    state: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: str
    role: str
