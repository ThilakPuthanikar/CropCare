from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database.database import Base


class DistrictRainfall(Base):
    __tablename__ = "district_rainfall"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), unique=True, nullable=False, index=True)
    labels_json = Column(Text, nullable=True)      # JSON array: ["Jan","Feb",...,"Dec"]
    rainfall_json = Column(Text, nullable=True)     # JSON array: [12.3, 45.6, ...]
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
