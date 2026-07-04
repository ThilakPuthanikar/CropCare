from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SchemeBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "national"
    beneficiary: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    documents_required: List[str] = []
    steps_to_apply: List[str] = []
    duration: Optional[str] = None
    official_link: Optional[str] = None
    icon: Optional[str] = "fas fa-hand-holding-heart"
    state: Optional[str] = None
    district: Optional[str] = None
    is_active: bool = True


class SchemeCreate(SchemeBase):
    pass


class SchemeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    beneficiary: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[str] = None
    documents_required: Optional[List[str]] = None
    steps_to_apply: Optional[List[str]] = None
    duration: Optional[str] = None
    official_link: Optional[str] = None
    icon: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    is_active: Optional[bool] = None


class SchemeInDB(SchemeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
