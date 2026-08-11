from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class LandLeaseInputSchema(BaseModel):
    state: str = Field(default="Karnataka", description="State name")
    district: str = Field(..., description="Karnataka District name")
    taluk: Optional[str] = Field(default=None)
    village: Optional[str] = Field(default=None)

    input_size: float = Field(..., gt=0, description="Land area numerical value")
    input_unit: str = Field(default="Acre", description="Unit of measurement: Acre, Hectare, or Guntha")

    land_type: Optional[str] = Field(default="Irrigated Agricultural Land")
    soil_type: Optional[str] = Field(default="Black / Clay Soil")
    current_use: Optional[str] = Field(default="Cultivated / Active Farm")
    intended_use: Optional[str] = Field(default="Commercial / Horticulture Crops")
    land_condition: Optional[str] = Field(default="Good / Flat Terrain")

    water_availability: str = Field(default="Regular Water (Perennial/Borewell)")
    water_source: Optional[str] = Field(default="Borewell")
    irrigation_type: Optional[str] = Field(default="Drip Irrigation")

    electricity_available: bool = Field(default=True)
    electricity_reliability: Optional[str] = Field(default="3-Phase Regular Supply")
    connection_type: Optional[str] = Field(default="Agricultural Free/Subsidized Grid")

    road_access: str = Field(default="Paved Road / Main Road")
    transport_access: Optional[str] = Field(default="Heavy Truck Accessible")
    distance_main_road_km: Optional[float] = Field(default=0.5, ge=0)
    distance_market_km: Optional[float] = Field(default=5.0, ge=0)

    infrastructure: List[str] = Field(default_factory=list, description="Selected infrastructure features")

    lease_duration_years: float = Field(default=1.0, ge=0.5, le=20.0)
    additional_notes: Optional[str] = Field(default=None)

    @validator("input_unit")
    def validate_unit(cls, v):
        valid = ["Acre", "Hectare", "Guntha", "Acres", "Hectares", "Gunthas"]
        if v not in valid:
            raise ValueError(f"Invalid unit. Must be one of: {valid}")
        return v


class LandLeaseResultSchema(BaseModel):
    report_id: str
    acres: float
    input_size: float
    input_unit: str
    district: str
    state: str

    base_rate_per_acre: float
    calculated_min_price: float
    calculated_max_price: float
    monthly_min_price: float
    monthly_max_price: float
    per_acre_min: float
    per_acre_max: float

    confidence_score: str
    confidence_reasons: List[str]
    positive_factors: List[Dict[str, Any]]
    negative_factors: List[Dict[str, Any]]

    ai_analysis: Dict[str, Any]
    created_at: str
