import requests
from datetime import date
from typing import Dict, Any, Optional
from .logger import logger


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"


def _request_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Weather API error: {e}")
        return {}


def _weather_code_to_text(weather_code: Optional[int]) -> str:
    weather_map = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Fog",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        56: "Freezing Drizzle",
        57: "Freezing Drizzle",
        61: "Light Rain",
        63: "Rain",
        65: "Heavy Rain",
        66: "Freezing Rain",
        67: "Freezing Rain",
        71: "Light Snow",
        73: "Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Rain Showers",
        81: "Rain Showers",
        82: "Heavy Rain Showers",
        85: "Snow Showers",
        86: "Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm",
    }
    return weather_map.get(weather_code or -1, "Unavailable")


# Hardcoded lat/lon for all 30 Karnataka districts.
# The Open-Meteo geocoding API fails for many administrative district names
# (e.g. "Bengaluru Urban", "Dakshina Kannada"), so we fall back to known coords.
KARNATAKA_DISTRICT_COORDS = {
    "Bagalkot":          {"latitude": 16.1691, "longitude": 75.6615, "name": "Bagalkot"},
    "Ballari":           {"latitude": 15.1394, "longitude": 76.9214, "name": "Ballari"},
    "Belagavi":          {"latitude": 15.8497, "longitude": 74.4977, "name": "Belagavi"},
    "Bengaluru Rural":   {"latitude": 13.2257, "longitude": 77.5750, "name": "Bengaluru Rural"},
    "Bengaluru Urban":   {"latitude": 12.9716, "longitude": 77.5946, "name": "Bengaluru Urban"},
    "Bidar":             {"latitude": 17.9104, "longitude": 77.5199, "name": "Bidar"},
    "Chamarajanagar":    {"latitude": 11.9261, "longitude": 76.9437, "name": "Chamarajanagar"},
    "Chikkaballapur":    {"latitude": 13.4355, "longitude": 77.7315, "name": "Chikkaballapur"},
    "Chikkamagaluru":    {"latitude": 13.3161, "longitude": 75.7720, "name": "Chikkamagaluru"},
    "Chitradurga":       {"latitude": 14.2226, "longitude": 76.3980, "name": "Chitradurga"},
    "Dakshina Kannada":  {"latitude": 12.8438, "longitude": 75.0109, "name": "Dakshina Kannada"},
    "Davanagere":        {"latitude": 14.4644, "longitude": 75.9218, "name": "Davanagere"},
    "Dharwad":           {"latitude": 15.4589, "longitude": 75.0078, "name": "Dharwad"},
    "Gadag":             {"latitude": 15.4166, "longitude": 75.6362, "name": "Gadag"},
    "Hassan":            {"latitude": 13.0068, "longitude": 76.0996, "name": "Hassan"},
    "Haveri":            {"latitude": 14.7951, "longitude": 75.3991, "name": "Haveri"},
    "Kalaburagi":        {"latitude": 17.3297, "longitude": 76.8343, "name": "Kalaburagi"},
    "Kodagu":            {"latitude": 12.4244, "longitude": 75.7382, "name": "Kodagu"},
    "Kolar":             {"latitude": 13.1362, "longitude": 78.1292, "name": "Kolar"},
    "Koppal":            {"latitude": 15.3550, "longitude": 76.1548, "name": "Koppal"},
    "Mandya":            {"latitude": 12.5218, "longitude": 76.8951, "name": "Mandya"},
    "Mysuru":            {"latitude": 12.2958, "longitude": 76.6394, "name": "Mysuru"},
    "Raichur":           {"latitude": 16.2120, "longitude": 77.3439, "name": "Raichur"},
    "Ramanagara":        {"latitude": 12.7159, "longitude": 77.2810, "name": "Ramanagara"},
    "Shivamogga":        {"latitude": 13.9299, "longitude": 75.5681, "name": "Shivamogga"},
    "Tumakuru":          {"latitude": 13.3379, "longitude": 77.1173, "name": "Tumakuru"},
    "Udupi":             {"latitude": 13.3409, "longitude": 74.7421, "name": "Udupi"},
    "Uttara Kannada":    {"latitude": 14.6819, "longitude": 74.6900, "name": "Uttara Kannada"},
    "Vijayapura":        {"latitude": 16.8302, "longitude": 75.7100, "name": "Vijayapura"},
    "Yadgir":            {"latitude": 16.7700, "longitude": 77.1383, "name": "Yadgir"},
}


def _geocode_location(location: str) -> Dict[str, Any]:
    raw_parts = [part.strip() for part in location.split(",") if part.strip()]
    district = raw_parts[0] if raw_parts else location.strip()
    state = raw_parts[1] if len(raw_parts) > 1 else ""

    candidates = [location.strip(), district]

    simplified_district = district
    for suffix in (" Urban", " Rural", " district", " District"):
        if simplified_district.endswith(suffix):
            simplified_district = simplified_district[: -len(suffix)].strip()

    if simplified_district and simplified_district not in candidates:
        candidates.append(simplified_district)

    if state:
        state_candidate = f"{district} {state}".strip()
        if state_candidate not in candidates:
            candidates.append(state_candidate)

        simplified_state_candidate = f"{simplified_district} {state}".strip()
        if simplified_district and simplified_state_candidate not in candidates:
            candidates.append(simplified_state_candidate)

    for candidate in candidates:
        geocode_response = _request_json(
            GEOCODE_URL,
            {
                "name": candidate,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        results = geocode_response.get("results")
        if isinstance(results, list) and results:
            return results[0]

    # Fallback: use hardcoded Karnataka district coordinates
    fallback = KARNATAKA_DISTRICT_COORDS.get(district)
    if fallback:
        return fallback

    # Also try the simplified district name for fallback
    if simplified_district and simplified_district != district:
        fallback = KARNATAKA_DISTRICT_COORDS.get(simplified_district)
        if fallback:
            return fallback

    return {}


def get_weather_data(api_key: str, location: str) -> Dict[Any, Any]:
    """
    Get current weather data using Open-Meteo and normalize it to the route's expected shape.
    """
    geo = _geocode_location(location)
    if not geo:
        return {"success": False}

    forecast_response = _request_json(
        FORECAST_URL,
        {
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto",
        },
    )

    current = forecast_response.get("current", {})
    if not current:
        return {"success": False}

    return {
        "location": {
            "name": geo.get("name", location),
            "country": geo.get("country", "India"),
        },
        "current": {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_descriptions": [
                _weather_code_to_text(current.get("weather_code"))
            ],
        },
    }


def get_forecast_data(api_key: str, location: str) -> Dict[Any, Any]:
    """
    Get 7-day forecast data using Open-Meteo and normalize it to the route's expected shape.
    """
    geo = _geocode_location(location)
    if not geo:
        return {"success": False}

    forecast_response = _request_json(
        FORECAST_URL,
        {
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 7,
            "timezone": "auto",
        },
    )

    daily = forecast_response.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    weather_codes = daily.get("weather_code", [])

    if not dates:
        return {"success": False}

    forecast: Dict[str, Any] = {}
    for index, date_value in enumerate(dates):
        forecast[str(date_value)] = {
            "date": date_value,
            "maxtemp": max_temps[index] if index < len(max_temps) else None,
            "mintemp": min_temps[index] if index < len(min_temps) else None,
            "hourly": [
                {
                    "weather_descriptions": [
                        _weather_code_to_text(
                            weather_codes[index] if index < len(weather_codes) else None
                        )
                    ]
                }
            ],
        }

    return {
        "location": {
            "name": geo.get("name", location),
            "country": geo.get("country", "India"),
        },
        "forecast": forecast,
    }


def get_historical_weather_data(
    api_key: str,
    location: str,
    start_date: date,
    end_date: date,
) -> Dict[Any, Any]:
    """
    Get historical daily weather data using Open-Meteo archive API.
    """
    geo = _geocode_location(location)
    if not geo:
        return {"success": False}

    historical_response = _request_json(
        HISTORICAL_URL,
        {
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "daily": "temperature_2m_mean,precipitation_sum",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timezone": "auto",
        },
    )

    daily = historical_response.get("daily", {})
    if not daily:
        return {"success": False}

    return {
        "location": {
            "name": geo.get("name", location),
            "country": geo.get("country", "India"),
        },
        "daily": daily,
    }
