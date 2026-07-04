from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..database.database import Base


class AIUsageHistory(Base):
    __tablename__ = "ai_usage_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feature_type = Column(String(100), nullable=False, index=True)  # crop_suggestion, input_suggestions, disease_diagnosis, crop_planner
    input_payload = Column(Text, nullable=True)   # JSON string storing inputs
    output_payload = Column(Text, nullable=False) # JSON string storing AI response
    created_at = Column(DateTime(timezone=True), server_default=func.now())
