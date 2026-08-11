from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database.database import Base


class LandLeaseEstimate(Base):
    __tablename__ = "land_lease_estimates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)

    # Location details
    state = Column(String(100), nullable=False, default="Karnataka")
    district = Column(String(100), nullable=False, index=True)
    taluk = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)

    # Land characteristics
    input_size = Column(Float, nullable=False)
    input_unit = Column(String(20), nullable=False, default="Acre")
    acres = Column(Float, nullable=False)  # Normalized area in Acres
    land_type = Column(String(100), nullable=True)
    soil_type = Column(String(100), nullable=True)
    current_use = Column(String(100), nullable=True)
    intended_use = Column(String(100), nullable=True)
    land_condition = Column(String(100), nullable=True)

    # Infrastructure & Utilities
    water_availability = Column(String(50), nullable=False, default="Rain-fed")
    water_source = Column(String(100), nullable=True)
    irrigation_type = Column(String(100), nullable=True)
    electricity_available = Column(Boolean, nullable=False, default=False)
    electricity_reliability = Column(String(100), nullable=True)
    connection_type = Column(String(100), nullable=True)
    road_access = Column(String(100), nullable=False, default="Gravel / Dirt Road")
    transport_access = Column(String(100), nullable=True)
    distance_main_road_km = Column(Float, nullable=True)
    distance_market_km = Column(Float, nullable=True)
    infrastructure_json = Column(Text, nullable=True)  # JSON string array of features

    # Term & Notes
    lease_duration_years = Column(Float, nullable=False, default=1.0)
    additional_notes = Column(Text, nullable=True)

    # Calculated Valuation Results
    base_rate_per_acre = Column(Float, nullable=False)
    calculated_min_price = Column(Float, nullable=False)
    calculated_max_price = Column(Float, nullable=False)
    confidence_score = Column(String(20), nullable=False, default="MODERATE")
    confidence_reasons_json = Column(Text, nullable=True)
    factors_json = Column(Text, nullable=True)  # Detailed positive/negative factors

    # AI Generated Assessment Payload
    ai_analysis_json = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to user
    user = relationship("User", backref="land_lease_estimates")
