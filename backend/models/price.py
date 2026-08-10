from sqlalchemy import Column, Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from ..database.database import Base


class Price(Base):
    __tablename__ = "mandi_prices"
    __table_args__ = (
        UniqueConstraint("crop_name", "district", "mandi_name", "price_date", name="uq_mandi_crop_market_week"),
    )

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(120), nullable=False)
    variety = Column(String(120), nullable=True)
    grade = Column(String(120), nullable=True)
    district = Column(String(120), nullable=False)
    mandi_name = Column(String(180), nullable=False)
    arrival = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    price_per_quintal = Column(Float, nullable=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    price_date = Column(Date, nullable=False)
    source = Column(String(50), default="KRAMA", nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Price(crop_name='{self.crop_name}', district='{self.district}', "
            f"mandi_name='{self.mandi_name}', price_date={self.price_date}, "
            f"price_per_quintal={self.price_per_quintal})>"
        )
