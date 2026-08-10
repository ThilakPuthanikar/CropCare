import re


KARNATAKA_DISTRICTS = {
    "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
    "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga",
    "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri",
    "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur",
    "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada",
    "Vijayapura", "Yadgir",
}

IRRIGATION_TYPES = {"Canal/Borewell", "Canal", "Borewell", "Rain-fed", "Drip", "Sprinkler"}


def is_valid_email(email: str) -> bool:
    email = (email or "").strip()
    return re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is not None


def is_valid_indian_phone(phone_number: str) -> bool:
    phone_number = (phone_number or "").strip()
    return re.fullmatch(r"[6-9]\d{9}", phone_number) is not None


def is_valid_name(name: str) -> bool:
    name = (name or "").strip()
    if len(name) < 2 or len(name) > 80:
        return False
    return re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", name) is not None


def is_strong_password(password: str) -> bool:
    password = password or ""
    if len(password) < 8:
        return False
    checks = [
        re.search(r"[a-z]", password),
        re.search(r"[A-Z]", password),
        re.search(r"\d", password),
        re.search(r"[^A-Za-z0-9]", password),
    ]
    return all(checks)


def is_valid_land_size(land_size: float) -> bool:
    return isinstance(land_size, (int, float)) and land_size > 0 and land_size <= 100000


def is_valid_district(district: str) -> bool:
    return (district or "").strip() in KARNATAKA_DISTRICTS


def is_valid_irrigation_type(irrigation_type: str) -> bool:
    return (irrigation_type or "").strip() in IRRIGATION_TYPES


SOIL_TYPES = {"Black Soil", "Red Soil", "Laterite Soil", "Alluvial Soil", "Sandy Soil", "Clay Soil"}
SOIL_TEXTURES = {"Sandy", "Loamy", "Clayey", "Silty", "Mixed"}
SEASONS = {"Kharif", "Rabi", "Summer"}
CROP_PURPOSES = {"Food Crop", "Cash Crop", "Fodder Crop", "Mixed"}
RISK_LEVELS = {"Low", "Medium", "High"}


def is_valid_ph(value: float) -> bool:
    return isinstance(value, (int, float)) and 0 <= value <= 14


def is_valid_npk(value: float) -> bool:
    return isinstance(value, (int, float)) and value >= 0


def is_valid_rainfall(value: float) -> bool:
    return isinstance(value, (int, float)) and value >= 0


def is_valid_soil_type(soil_type: str) -> bool:
    return (soil_type or "").strip() in SOIL_TYPES


def is_valid_soil_texture(texture: str) -> bool:
    return (texture or "").strip() in SOIL_TEXTURES


def is_valid_season(season: str) -> bool:
    return (season or "").strip() in SEASONS


def is_valid_purpose(purpose: str) -> bool:
    return (purpose or "").strip() in CROP_PURPOSES


def is_valid_risk_preference(risk: str) -> bool:
    return (risk or "").strip() in RISK_LEVELS
