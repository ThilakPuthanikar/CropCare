from typing import Dict, Any, List, Tuple
from ..schemas.land_lease import LandLeaseInputSchema


# Unit Conversion Helpers
def normalize_to_acres(size: float, unit: str) -> float:
    unit_lower = unit.lower().strip()
    if "hectare" in unit_lower:
        return size * 2.47105
    elif "guntha" in unit_lower:
        return size * 0.025  # 40 Gunthas = 1 Acre
    else: # Acre
        return size


# District Tier Base Rates per Acre/Year in Karnataka (in INR)
DISTRICT_BASE_RATES: Dict[str, float] = {
    # Tier 1 - Metro / Peri-Urban / High Land Value
    "bengaluru urban": 48000.0,
    "bengaluru rural": 42000.0,
    "ramanagara": 38000.0,

    # Tier 2 - Highly Irrigated & Fertile Basins (Mandya, Cauvery & Malnad Belt)
    "mandya": 35000.0,
    "mysuru": 32000.0,
    "shivamogga": 30000.0,
    "belagavi": 30000.0,
    "davanagere": 28000.0,
    "hassan": 28000.0,
    "dakshina kannada": 32000.0,
    "udupi": 30000.0,
    "uttara kannada": 28000.0,
    "chikkamagaluru": 32000.0,
    "kodagu": 35000.0,

    # Tier 3 - Mixed Rainfed & Semi-Arid Agricultural Districts
    "tumakuru": 22000.0,
    "dharwad": 24000.0,
    "haveri": 22000.0,
    "gadag": 20000.0,
    "vijayanagara": 24000.0,
    "ballari": 22000.0,
    "chikkaballapur": 24000.0,
    "kolar": 24000.0,
    "chitradurga": 20000.0,

    # Tier 4 - Northern Dryland & Low Rainfall Belts
    "bagalkot": 18000.0,
    "vijayapura": 18000.0,
    "kalaburagi": 16000.0,
    "bidar": 17000.0,
    "raichur": 18000.0,
    "koppal": 18000.0,
    "yadgir": 15000.0,
    "chamarajanagar": 20000.0,
}

DEFAULT_BASE_RATE: float = 22000.0


def get_base_rate_for_district(district_name: str) -> float:
    normalized = (district_name or "").strip().lower()
    return DISTRICT_BASE_RATES.get(normalized, DEFAULT_BASE_RATE)


def calculate_land_valuation(input_data: LandLeaseInputSchema) -> Dict[str, Any]:
    """
    Computes deterministic land lease valuation range, positive/negative drivers,
    and confidence score for Karnataka land parameters.
    """
    acres = normalize_to_acres(input_data.input_size, input_data.input_unit)
    acres = max(0.01, round(acres, 3))

    base_rate = get_base_rate_for_district(input_data.district)
    total_multiplier = 1.0

    positive_factors: List[Dict[str, Any]] = []
    negative_factors: List[Dict[str, Any]] = []

    # 1. Water Availability
    water_val = (input_data.water_availability or "").lower()
    if any(k in water_val for k in ["year-round", "perennial", "regular", "canal"]):
        total_multiplier *= 1.35
        positive_factors.append({
            "category": "Water & Irrigation",
            "impact": "+35%",
            "description": "Perennial / Year-round dependable water supply",
            "is_positive": True
        })
    elif "seasonal" in water_val:
        total_multiplier *= 1.08
        positive_factors.append({
            "category": "Water & Irrigation",
            "impact": "+8%",
            "description": "Seasonal water availability during monsoon/kharif",
            "is_positive": True
        })
    elif "rain" in water_val or "none" in water_val or "dry" in water_val:
        total_multiplier *= 0.80
        negative_factors.append({
            "category": "Water & Irrigation",
            "impact": "-20%",
            "description": "Rain-fed land without dedicated irrigation facility",
            "is_positive": False
        })

    # Irrigation system bonus
    irrigation_val = (input_data.irrigation_type or "").lower()
    if any(k in irrigation_val for k in ["drip", "sprinkler", "micro"]):
        total_multiplier *= 1.12
        positive_factors.append({
            "category": "Irrigation Equipment",
            "impact": "+12%",
            "description": "Modern Drip / Micro-irrigation network installed",
            "is_positive": True
        })
    elif "flood" in irrigation_val or "canal" in irrigation_val:
        total_multiplier *= 1.05
        positive_factors.append({
            "category": "Irrigation Equipment",
            "impact": "+5%",
            "description": "Surface channel / flood irrigation setup",
            "is_positive": True
        })

    # 2. Electricity
    if input_data.electricity_available:
        rel_val = (input_data.electricity_reliability or "").lower()
        if "3-phase" in rel_val or "regular" in rel_val or "dedicated" in rel_val:
            total_multiplier *= 1.15
            positive_factors.append({
                "category": "Electricity Supply",
                "impact": "+15%",
                "description": "3-Phase reliable agricultural power connection",
                "is_positive": True
            })
        else:
            total_multiplier *= 1.05
            positive_factors.append({
                "category": "Electricity Supply",
                "impact": "+5%",
                "description": "Standard electrical grid connectivity",
                "is_positive": True
            })
    else:
        total_multiplier *= 0.88
        negative_factors.append({
            "category": "Electricity Supply",
            "impact": "-12%",
            "description": "No grid electricity connection on land parcel",
            "is_positive": False
        })

    # 3. Road Access & Transport
    road_val = (input_data.road_access or "").lower()
    if any(k in road_val for k in ["paved", "highway", "main road", "tar"]):
        total_multiplier *= 1.18
        positive_factors.append({
            "category": "Road Infrastructure",
            "impact": "+18%",
            "description": "Direct frontage to paved/main tar road",
            "is_positive": True
        })
    elif any(k in road_val for k in ["gravel", "all-weather", "dirt"]):
        total_multiplier *= 1.08
        positive_factors.append({
            "category": "Road Infrastructure",
            "impact": "+8%",
            "description": "All-weather gravel road connectivity",
            "is_positive": True
        })
    elif any(k in road_val for k in ["mud", "narrow", "no road"]):
        total_multiplier *= 0.90
        negative_factors.append({
            "category": "Road Infrastructure",
            "impact": "-10%",
            "description": "Mud track / limited vehicular road access",
            "is_positive": False
        })

    transport_val = (input_data.transport_access or "").lower()
    if "truck" in transport_val or "heavy" in transport_val:
        total_multiplier *= 1.08
        positive_factors.append({
            "category": "Transport Accessibility",
            "impact": "+8%",
            "description": "Accessible for heavy commercial trucks and multi-ton transport",
            "is_positive": True
        })

    # 4. Infrastructure Features
    infra_list = [infra.lower() for infra in (input_data.infrastructure or [])]
    if any("fence" in i or "fencing" in i or "gate" in i for i in infra_list):
        total_multiplier *= 1.08
        positive_factors.append({
            "category": "Security",
            "impact": "+8%",
            "description": "Perimeter fencing / gated security protection",
            "is_positive": True
        })
    if any("pump" in i or "solar" in i or "borewell" in i for i in infra_list):
        total_multiplier *= 1.08
        positive_factors.append({
            "category": "On-site Equipment",
            "impact": "+8%",
            "description": "Motor pump set / Solar pump setup included",
            "is_positive": True
        })
    if any("storage" in i or "house" in i or "godown" in i or "shed" in i for i in infra_list):
        total_multiplier *= 1.10
        positive_factors.append({
            "category": "Structures",
            "impact": "+10%",
            "description": "Storage shed / Farmhouse / Godown available on land",
            "is_positive": True
        })
    if any("polyhouse" in i or "shade" in i or "greenhouse" in i for i in infra_list):
        total_multiplier *= 1.25
        positive_factors.append({
            "category": "High-Tech Structures",
            "impact": "+25%",
            "description": "Polyhouse / Protected shade net structure",
            "is_positive": True
        })

    # 5. Soil & Terrain
    soil_val = (input_data.soil_type or "").lower()
    if any(k in soil_val for k in ["black", "cotton", "loamy", "alluvial", "fertile"]):
        total_multiplier *= 1.10
        positive_factors.append({
            "category": "Soil Quality",
            "impact": "+10%",
            "description": "Highly fertile soil (Black Cotton / Deep Loam)",
            "is_positive": True
        })
    elif any(k in soil_val for k in ["saline", "rocky", "gravelly", "sandy"]):
        total_multiplier *= 0.88
        negative_factors.append({
            "category": "Soil Quality",
            "impact": "-12%",
            "description": "Rocky or low-retention soil type",
            "is_positive": False
        })

    # 6. Intended Crop / Land Use
    use_val = (input_data.intended_use or "").lower()
    if any(k in use_val for k in ["commercial", "horticulture", "spices", "arecanut", "polyhouse", "exotic"]):
        total_multiplier *= 1.15
        positive_factors.append({
            "category": "Cropping Potential",
            "impact": "+15%",
            "description": "High yield commercial horticulture / cash crop potential",
            "is_positive": True
        })
    elif any(k in use_val for k in ["sugarcane", "paddy", "maize", "pulses", "field"]):
        total_multiplier *= 1.05
        positive_factors.append({
            "category": "Cropping Potential",
            "impact": "+5%",
            "description": "Standard intensive agricultural crop cultivation",
            "is_positive": True
        })

    # 7. Lease Duration Discount (Long Term Stability)
    if input_data.lease_duration_years >= 3.0:
        total_multiplier *= 0.95
        positive_factors.append({
            "category": "Lease Term",
            "impact": "-5% (Tenant Benefit)",
            "description": "Long-term multi-year lease stability discount applied",
            "is_positive": True
        })

    # Final Calculation per Acre
    calculated_base_rate = base_rate * total_multiplier
    per_acre_min = round(calculated_base_rate * 0.88, -2) # -12%
    per_acre_max = round(calculated_base_rate * 1.15, -2) # +15%

    # Total Annual Lease
    calculated_min_price = round(per_acre_min * acres, -2)
    calculated_max_price = round(per_acre_max * acres, -2)

    # Ensure minimum sanity bounds
    calculated_min_price = max(3000.0 * acres, calculated_min_price)
    calculated_max_price = max(calculated_min_price + (1000.0 * acres), calculated_max_price)

    # Monthly Breakdown
    monthly_min_price = round(calculated_min_price / 12.0, -1)
    monthly_max_price = round(calculated_max_price / 12.0, -1)

    # Confidence Score Evaluation
    confidence_reasons: List[str] = []
    points = 0

    if input_data.district:
        points += 2
        confidence_reasons.append("Exact Karnataka district regional baseline applied.")
    if input_data.taluk or input_data.village:
        points += 1
        confidence_reasons.append("Specific sub-regional location details provided.")
    if input_data.water_availability and input_data.water_source:
        points += 2
        confidence_reasons.append("Comprehensive water and irrigation parameters specified.")
    if input_data.electricity_available is not None:
        points += 1
        confidence_reasons.append("Electricity grid connectivity and reliability validated.")
    if input_data.road_access:
        points += 1
        confidence_reasons.append("Road frontage and logistics accessibility verified.")
    if input_data.infrastructure and len(input_data.infrastructure) > 0:
        points += 1
        confidence_reasons.append("Physical infrastructure and equipment features included.")

    if points >= 6:
        confidence_score = "HIGH"
    elif points >= 4:
        confidence_score = "MODERATE"
    else:
        confidence_score = "LOW"
        confidence_reasons.append("Additional local details can further improve price precision.")

    return {
        "acres": acres,
        "base_rate_per_acre": round(base_rate, 2),
        "calculated_min_price": float(calculated_min_price),
        "calculated_max_price": float(calculated_max_price),
        "monthly_min_price": float(monthly_min_price),
        "monthly_max_price": float(monthly_max_price),
        "per_acre_min": float(per_acre_min),
        "per_acre_max": float(per_acre_max),
        "confidence_score": confidence_score,
        "confidence_reasons": confidence_reasons,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
    }
