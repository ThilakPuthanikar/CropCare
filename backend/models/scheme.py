from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database.database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False, default="national")
    beneficiary = Column(String(100))
    benefits = Column(Text)
    eligibility = Column(Text)
    documents_required = Column(Text)
    steps_to_apply = Column(Text)
    duration = Column(String(255))
    official_link = Column(String(500))
    icon = Column(String(100), default="fas fa-hand-holding-heart")
    state = Column(String(100))
    district = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
