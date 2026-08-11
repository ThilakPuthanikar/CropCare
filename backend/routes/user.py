import logging
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, date, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from ..database.database import get_db
from ..models.user import User
from ..models.ad import Ad
from ..models.crop_plan import CropPlan
from ..models.district_rainfall import DistrictRainfall
from ..models.ai_history import AIUsageHistory
from ..models.price import Price
from ..models.scheme import Scheme
from ..utils.auth import get_current_user
from ..utils.rate_limit import enforce_rate_limit
from ..utils.ai import (
    get_crop_suggestion,
    get_structured_crop_suggestion,
    get_disease_diagnosis as generate_disease_diagnosis,
    generate_ai_crop_plan,
)
from ..utils.crop_planner import (
    PLANNER_CROP_LIBRARY,
    build_crop_plan_payload,
    get_crop_planner_config,
    get_live_plan_reminder,
    parse_date_value,
    process_ai_crop_plan,
    serialize_crop_plan,
)
from ..utils.schemes import scheme_to_payload
from ..utils.validation import (
    is_valid_district,
    is_valid_indian_phone,
    is_valid_irrigation_type,
    is_valid_land_size,
    is_valid_name,
    is_valid_npk,
    is_valid_ph,
    is_valid_purpose,
    is_valid_rainfall,
    is_valid_risk_preference,
    is_valid_season,
    is_valid_soil_texture,
    is_valid_soil_type,
)
from ..utils.weather import (
    get_weather_data as fetch_current_weather_data,
    get_forecast_data,
    get_historical_weather_data,
)
from ..config.settings import settings
from pypdf import PdfReader

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

PROFILE_UPLOAD_DIR = Path("static/uploads/profiles")
PROFILE_UPLOAD_ROUTE_PREFIX = "/static/uploads/profiles/"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_PROFILE_PHOTO_SIZE = 5 * 1024 * 1024


def _get_active_crop_plan(db: Session, user_id: int) -> Optional[CropPlan]:
    return (
        db.query(CropPlan)
        .filter(CropPlan.user_id == user_id, CropPlan.harvest_date >= date.today())
        .order_by(CropPlan.harvest_date.desc(), CropPlan.created_at.desc())
        .first()
    )


def _build_chatbase_user_id(user_id: int) -> str:
    digest = hmac.new(
        settings.JWT_SECRET.encode("utf-8"),
        f"chatbase:{user_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"cbu_{digest}"


def _build_user_template_context(request: Request, current_user: User, **extra_context):
    context = {
        "request": request,
        "user": current_user,
        "chatbot_id": settings.CHATBOT_ID,
        "chatbase_user_id": _build_chatbase_user_id(current_user.id),
    }
    context.update(extra_context)
    return context

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "user/dashboard.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/profile.html",
        _build_user_template_context(request, current_user),
    )


def _delete_old_profile_photo(photo_path: Optional[str]) -> None:
    if not photo_path or not photo_path.startswith(PROFILE_UPLOAD_ROUTE_PREFIX):
        return

    disk_path = Path(photo_path.lstrip("/"))
    try:
        upload_root = PROFILE_UPLOAD_DIR.resolve()
        resolved_disk_path = disk_path.resolve()
    except Exception:
        return

    if upload_root not in resolved_disk_path.parents:
        return

    if resolved_disk_path.exists():
        resolved_disk_path.unlink(missing_ok=True)


async def _save_profile_photo(file_obj: UploadFile, user_id: int) -> str:
    if file_obj.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, or WEBP images are allowed.",
        )

    file_bytes = await file_obj.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    if len(file_bytes) > MAX_PROFILE_PHOTO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile photo size must be under 5MB.",
        )

    PROFILE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = ALLOWED_IMAGE_TYPES[file_obj.content_type]
    filename = f"user_{user_id}_{uuid.uuid4().hex[:10]}{extension}"
    output_path = PROFILE_UPLOAD_DIR / filename
    output_path.write_bytes(file_bytes)
    return f"{PROFILE_UPLOAD_ROUTE_PREFIX}{filename}"


@router.put("/profile")
async def update_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    name = (form_data.get("name") or "").strip()
    phone_number = (form_data.get("phone_number") or "").strip()
    district = form_data.get("district")
    land_size = form_data.get("land_size")
    irrigation_type = form_data.get("irrigation_type")
    remove_photo = str(form_data.get("remove_profile_photo") or "").lower() == "true"
    profile_photo = form_data.get("profile_photo")

    if name:
        if not is_valid_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be 2-80 characters and contain letters and spaces only.",
            )
        current_user.name = name
    if phone_number:
        if not is_valid_indian_phone(phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number must be 10 digits and start with 6, 7, 8, or 9.",
            )
        existing_phone_user = (
            db.query(User.id)
            .filter(User.phone_number == phone_number, User.id != current_user.id)
            .first()
        )
        if existing_phone_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use.",
            )
        current_user.phone_number = phone_number
    if district:
        if not is_valid_district(district):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please select a valid Karnataka district.",
            )
        current_user.district = district
    if land_size:
        try:
            parsed_land_size = float(land_size)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land size must be a valid number.",
            )
        if not is_valid_land_size(parsed_land_size):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land size must be greater than zero.",
            )
        current_user.land_size = parsed_land_size
    if irrigation_type:
        if not is_valid_irrigation_type(irrigation_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please select a valid irrigation type.",
            )
        current_user.irrigation_type = irrigation_type

    if remove_photo:
        _delete_old_profile_photo(current_user.profile_photo)
        current_user.profile_photo = None

    if hasattr(profile_photo, "filename") and profile_photo.filename:
        old_photo = current_user.profile_photo
        current_user.profile_photo = await _save_profile_photo(profile_photo, current_user.id)
        if old_photo and old_photo != current_user.profile_photo:
            _delete_old_profile_photo(old_photo)

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "state": current_user.state,
            "district": current_user.district,
            "land_size": current_user.land_size,
            "irrigation_type": current_user.irrigation_type,
            "profile_photo": current_user.profile_photo,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        },
    }

@router.get("/soil-library", response_class=HTMLResponse)
async def soil_library(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/soil_library.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/weather", response_class=HTMLResponse)
async def weather_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/weather.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/crop-recommendation", response_class=HTMLResponse)
async def crop_recommendation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/crop_recommendation.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/input-suggestions", response_class=HTMLResponse)
async def input_suggestions(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/input_suggestions.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/disease-diagnosis", response_class=HTMLResponse)
async def disease_diagnosis(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/disease_diagnosis.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/crop-planner", response_class=HTMLResponse)
async def crop_planner(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active_plan = _get_active_crop_plan(db, current_user.id)
    return templates.TemplateResponse(
        "user/crop_planner.html",
        _build_user_template_context(
            request,
            current_user,
            active_plan=serialize_crop_plan(active_plan) if active_plan else None,
            planner_crops=[
                {"value": key, "label": value["label"], "duration_days": value["duration_days"]}
                for key, value in PLANNER_CROP_LIBRARY.items()
            ],
        ),
    )

@router.get("/mandi-tracking", response_class=HTMLResponse)
async def mandi_tracking(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/mandi_tracking.html",
        _build_user_template_context(request, current_user),
    )

@router.get("/proxy-krama", response_class=HTMLResponse)
async def proxy_krama():
    """
    Server-side proxy for the official KRAMA portal.
    Fetches the live HTML asynchronously from https://krama.karnataka.gov.in/Reports/Main_rep and injects a <base> tag
    so it embeds cleanly in the user's dashboard iframe without X-Frame-Options or SameSite=Lax blocking.
    """
    import asyncio
    import requests
    try:
        def fetch_krama():
            return requests.get("https://krama.karnataka.gov.in/Reports/Main_rep", verify=False, timeout=25, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

        r = await asyncio.to_thread(fetch_krama)
        html_content = r.text

        # Inject base tag and frame protection so KRAMA loads images/styles without busting out of the iframe
        safeguard = '<head><base href="https://krama.karnataka.gov.in/Reports/Main_rep"><script>window.top = window.self; window.parent = window.self;</script>'
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", safeguard)
        elif "<HEAD>" in html_content:
            html_content = html_content.replace("<HEAD>", safeguard)
        else:
            html_content = f'{safeguard}{html_content}'

        html_content = html_content.replace("window.top", "window.self").replace("top.location", "self.location").replace("parent.location", "self.location")

        response = HTMLResponse(content=html_content, status_code=200)
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response
    except Exception as exc:
        logger.error("Error proxying KRAMA portal: %s", exc)
        return HTMLResponse(
            content=f"""
            <div style="font-family: 'Inter', sans-serif; padding: 40px; text-align: center; color: #1e293b;">
                <h3 style="color: #15803d; margin-bottom: 12px;">Official Karnataka KRAMA Portal</h3>
                <p style="margin-bottom: 24px; color: #64748b;">Live connection temporarily unavailable or experiencing high traffic from Karnataka state servers.</p>
                <a href="https://krama.karnataka.gov.in/Reports/Main_rep" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #16a34a; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                    Open Official Portal in New Tab &rarr;
                </a>
            </div>
            """,
            status_code=200
        )


@router.get("/gov-schemes", response_class=HTMLResponse)
async def gov_schemes(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "user/gov_schemes.html",
        _build_user_template_context(request, current_user),
    )


    # backend/routes/user.py

# ... (other imports) ...



# Define a Pydantic model for the response
class ReminderData(BaseModel):
    message: Optional[str] = None
    time: Optional[str] = None

class WeatherData(BaseModel):
    temperature: Optional[float] = None
    condition: Optional[str] = None
    humidity: Optional[float] = None

class AdData(BaseModel):
    content: str
    type: str # e.g., 'offer', 'announcement', 'tip', 'product'

class DashboardResponse(BaseModel):
    reminder: Optional[ReminderData] = None
    weather: Optional[WeatherData] = None
    ads: List[AdData] = []


def _build_weather_location(current_user: User) -> str:
    district = (current_user.district or "").strip()
    state = (current_user.state or "Karnataka").strip()

    if district:
        return f"{district}, {state}, India"

    return f"{state}, India"


def _pick_condition(source: Optional[dict], fallback: str = "Unavailable") -> str:
    if not isinstance(source, dict):
        return fallback

    descriptions = source.get("weather_descriptions")
    if isinstance(descriptions, list) and descriptions:
        return str(descriptions[0])

    return fallback


def _parse_dashboard_weather(api_response: dict) -> Optional[WeatherData]:
    if not isinstance(api_response, dict) or api_response.get("success") is False:
        return None

    current = api_response.get("current")
    if not isinstance(current, dict):
        return None

    temperature = current.get("temperature")
    humidity = current.get("humidity")

    if temperature is None or humidity is None:
        return None

    return WeatherData(
        temperature=float(temperature),
        condition=_pick_condition(current),
        humidity=float(humidity),
    )


def _decode_text_bytes(contents: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return contents.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return ""


def _extract_pdf_text(contents: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(contents))
    except Exception:
        return ""

    extracted_pages = []
    for page in reader.pages:
        try:
            extracted_pages.append(page.extract_text() or "")
        except Exception:
            continue

    return "\n".join(part.strip() for part in extracted_pages if part.strip()).strip()


def _build_image_data_url(content_type: str, contents: bytes) -> str:
    encoded = base64.b64encode(contents).decode("ascii")
    return f"data:{content_type};base64,{encoded}"

# ... (existing routes) ...

@router.get("/dashboard-data", response_model=DashboardResponse)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches dynamic data for the user dashboard (reminder, weather, ads).
    """
    # Example logic - replace with actual implementations

    active_plan = _get_active_crop_plan(db, current_user.id)
    reminder_payload = get_live_plan_reminder(active_plan) if active_plan else {
        "message": "No active crop plan is running right now. Create one in Crop Planner to receive live reminders.",
        "time": None,
    }
    reminder = ReminderData(
        message=reminder_payload.get("message"),
        time=reminder_payload.get("time"),
    )

    # 2. Fetch live weather based on the user's district
    weather_location = _build_weather_location(current_user)
    weather_response = fetch_current_weather_data(
        settings.WEATHERSTACK_API_KEY,
        weather_location,
    )
    weather = _parse_dashboard_weather(weather_response)

    # 3. Fetch active ads
    active_ads = db.query(Ad).filter(Ad.is_active == True).all()
    ads_list = [AdData(content=ad.content, type='announcement') for ad in active_ads] # Simplified mapping

    return DashboardResponse(reminder=reminder, weather=weather, ads=ads_list)

# backend/routes/user.py

# ... (other imports) ...



# Define Pydantic models for the response
class CurrentWeather(BaseModel):
    temperature: float
    condition: str
    humidity: float
    wind_speed: float

class ForecastDay(BaseModel):
    date: str # e.g., "2026-03-05"
    max_temp: float
    min_temp: float
    condition: str

class WeatherAnalytics(BaseModel):
    labels: List[str] = []
    rainfall: List[float] = []
    temperature: List[float] = []

class WeatherResponse(BaseModel):
    current: Optional[CurrentWeather] = None
    forecast: List[ForecastDay] = []
    analytics: Optional[WeatherAnalytics] = None


def _parse_current_weather(api_response: dict) -> Optional[CurrentWeather]:
    if not isinstance(api_response, dict) or api_response.get("success") is False:
        return None

    current = api_response.get("current")
    if not isinstance(current, dict):
        return None

    temperature = current.get("temperature")
    humidity = current.get("humidity")
    wind_speed = current.get("wind_speed")

    if temperature is None or humidity is None or wind_speed is None:
        return None

    return CurrentWeather(
        temperature=float(temperature),
        condition=_pick_condition(current),
        humidity=float(humidity),
        wind_speed=float(wind_speed),
    )


def _parse_forecast_weather(api_response: dict) -> List[ForecastDay]:
    if not isinstance(api_response, dict) or api_response.get("success") is False:
        return []

    forecast = api_response.get("forecast")
    if not isinstance(forecast, dict):
        return []

    forecast_days: List[ForecastDay] = []

    for date_key, day_data in sorted(forecast.items()):
        if not isinstance(day_data, dict):
            continue

        max_temp = day_data.get("maxtemp")
        min_temp = day_data.get("mintemp")
        if max_temp is None or min_temp is None:
            continue

        condition = "Forecast"
        hourly = day_data.get("hourly")
        if isinstance(hourly, list) and hourly:
            first_hour = hourly[0] if isinstance(hourly[0], dict) else {}
            condition = _pick_condition(first_hour, fallback=condition)

        date_value = day_data.get("date") or date_key
        try:
            parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            parsed_date = str(date_key)

        forecast_days.append(
            ForecastDay(
                date=parsed_date,
                max_temp=float(max_temp),
                min_temp=float(min_temp),
                condition=condition,
            )
        )

    return forecast_days[:7]


def _parse_weather_analytics(api_response: dict) -> Optional[WeatherAnalytics]:
    if not isinstance(api_response, dict) or api_response.get("success") is False:
        return None

    daily = api_response.get("daily")
    if not isinstance(daily, dict):
        return None

    dates = daily.get("time", [])
    rainfall_values = daily.get("precipitation_sum", [])
    temperature_values = daily.get("temperature_2m_mean", [])

    if not dates:
        return None

    monthly_data = {}
    for index, date_value in enumerate(dates):
        try:
            parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d")
        except ValueError:
            continue

        month_key = parsed_date.strftime("%Y-%m")
        month_label = parsed_date.strftime("%b")
        rainfall = rainfall_values[index] if index < len(rainfall_values) else 0
        temperature = temperature_values[index] if index < len(temperature_values) else None

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "label": month_label,
                "rainfall": 0.0,
                "temperature_total": 0.0,
                "temperature_count": 0,
            }

        monthly_data[month_key]["rainfall"] += float(rainfall or 0)
        if temperature is not None:
            monthly_data[month_key]["temperature_total"] += float(temperature)
            monthly_data[month_key]["temperature_count"] += 1

    labels: List[str] = []
    rainfall: List[float] = []
    temperature: List[float] = []

    for month_key in sorted(monthly_data.keys()):
        month_entry = monthly_data[month_key]
        labels.append(month_entry["label"])
        rainfall.append(round(month_entry["rainfall"], 1))

        if month_entry["temperature_count"] > 0:
            average_temp = month_entry["temperature_total"] / month_entry["temperature_count"]
            temperature.append(round(average_temp, 1))
        else:
            temperature.append(0.0)

    return WeatherAnalytics(labels=labels, rainfall=rainfall, temperature=temperature)

# ... (existing routes like profile, soil-library, etc.) ...

@router.get("/weather-data", response_model=WeatherResponse)
async def get_weather_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches live weather data for the user's district.
    """
    weather_location = _build_weather_location(current_user)

    current_response = fetch_current_weather_data(
        settings.WEATHERSTACK_API_KEY,
        weather_location,
    )
    forecast_response = get_forecast_data(
        settings.WEATHERSTACK_API_KEY,
        weather_location,
    )
    analytics_response = get_historical_weather_data(
        settings.WEATHERSTACK_API_KEY,
        weather_location,
        start_date=date.today() - timedelta(days=364),
        end_date=date.today(),
    )

    current_weather = _parse_current_weather(current_response)
    forecast_list = _parse_forecast_weather(forecast_response)
    analytics = _parse_weather_analytics(analytics_response)

    # Write-through: cache rainfall data for this district
    district_name = (current_user.district or "").strip()
    if district_name and analytics:
        _upsert_district_rainfall(db, district_name, analytics.labels, analytics.rainfall)

    return WeatherResponse(
        current=current_weather,
        forecast=forecast_list,
        analytics=analytics,
    )


def _upsert_district_rainfall(
    db: Session,
    district: str,
    labels: List[str],
    rainfall: List[float],
) -> None:
    """Insert or update the rainfall cache row for a district."""
    try:
        row = db.query(DistrictRainfall).filter(
            DistrictRainfall.district == district
        ).first()

        labels_str = json.dumps(labels)
        rainfall_str = json.dumps(rainfall)
        now = datetime.now(timezone.utc)

        if row:
            row.labels_json = labels_str
            row.rainfall_json = rainfall_str
            row.fetched_at = now
        else:
            row = DistrictRainfall(
                district=district,
                labels_json=labels_str,
                rainfall_json=rainfall_str,
                fetched_at=now,
            )
            db.add(row)

        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to cache district rainfall for {district}: {exc}")


class DistrictRainfallResponse(BaseModel):
    district: str
    labels: List[str] = []
    rainfall: List[float] = []
    total_rainfall: float = 0.0
    cached: bool = False


@router.get("/district-rainfall", response_model=DistrictRainfallResponse)
async def get_district_rainfall(
    district: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns monthly rainfall data for a district.
    Serves from DB cache if fresh (< 7 days), otherwise fetches from API and caches.
    """
    district_name = (district or current_user.district or "").strip()
    if not district_name:
        raise HTTPException(status_code=400, detail="No district specified.")

    # Check cache
    cache_row = db.query(DistrictRainfall).filter(
        DistrictRainfall.district == district_name
    ).first()

    if cache_row and cache_row.fetched_at:
        # Handle naive datetimes if sqlite returned naive
        fetched_at = cache_row.fetched_at
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - fetched_at
        if age < timedelta(days=7) and cache_row.labels_json and cache_row.rainfall_json:
            labels = json.loads(cache_row.labels_json)
            rainfall = json.loads(cache_row.rainfall_json)
            return DistrictRainfallResponse(
                district=district_name,
                labels=labels,
                rainfall=rainfall,
                total_rainfall=round(sum(rainfall), 1),
                cached=True,
            )

    # Fetch fresh data from API
    location_str = f"{district_name}, Karnataka, India"
    analytics_response = get_historical_weather_data(
        settings.WEATHERSTACK_API_KEY,
        location_str,
        start_date=date.today() - timedelta(days=364),
        end_date=date.today(),
    )
    analytics = _parse_weather_analytics(analytics_response)

    if not analytics or not analytics.labels:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch rainfall data for {district_name}.",
        )

    # Cache the result
    _upsert_district_rainfall(db, district_name, analytics.labels, analytics.rainfall)

    return DistrictRainfallResponse(
        district=district_name,
        labels=analytics.labels,
        rainfall=analytics.rainfall,
        total_rainfall=round(sum(analytics.rainfall), 1),
        cached=False,
    )


def _log_ai_history(
    db: Session,
    user_id: int,
    feature_type: str,
    input_payload: Any,
    output_payload: Any,
) -> None:
    """Helper to log AI usage to ai_usage_history without breaking API requests if DB error occurs."""
    try:
        input_str = (
            json.dumps(input_payload, default=str)
            if isinstance(input_payload, (dict, list))
            else str(input_payload or "")
        )
        output_str = (
            json.dumps(output_payload, default=str)
            if isinstance(output_payload, (dict, list))
            else str(output_payload or "")
        )

        history_record = AIUsageHistory(
            user_id=user_id,
            feature_type=feature_type,
            input_payload=input_str,
            output_payload=output_str,
        )
        db.add(history_record)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to log AI history for user {user_id} ({feature_type}): {exc}")


class AIHistoryItem(BaseModel):
    id: int
    feature_type: str
    input_payload: dict
    output_payload: dict
    created_at: str


class AIHistoryResponse(BaseModel):
    history: List[AIHistoryItem]


@router.get("/ai-history", response_model=AIHistoryResponse)
async def get_ai_history(
    feature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the top 20 most recent AI usage records for the specified feature for the current user.
    Strictly isolated per user.
    """
    records = (
        db.query(AIUsageHistory)
        .filter(
            AIUsageHistory.user_id == current_user.id,
            AIUsageHistory.feature_type == feature.strip().lower(),
        )
        .order_by(AIUsageHistory.created_at.desc())
        .limit(20)
        .all()
    )

    history_items = []
    for rec in records:
        try:
            in_dict = json.loads(rec.input_payload) if rec.input_payload else {}
        except Exception:
            in_dict = {"raw": rec.input_payload}

        try:
            out_dict = json.loads(rec.output_payload) if rec.output_payload else {}
        except Exception:
            out_dict = {"raw": rec.output_payload}

        history_items.append(
            AIHistoryItem(
                id=rec.id,
                feature_type=rec.feature_type,
                input_payload=in_dict if isinstance(in_dict, dict) else {"data": in_dict},
                output_payload=out_dict if isinstance(out_dict, dict) else {"data": out_dict},
                created_at=rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else "",
            )
        )

    return AIHistoryResponse(history=history_items)


# backend/routes/user.py

# ... (other imports, including User, get_current_user, db dependency, etc.) ...

class CropRecommendationResponse(BaseModel):
    recommended_crop: str
    reason: str

# ... (existing routes like profile, soil-library, weather, etc.) ...

@router.post("/crop-recommendation", response_model=CropRecommendationResponse)
async def get_crop_recommendation(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    soil_report: UploadFile = File(None), # Optional file upload
    soil_details: str = Form(None),      # Optional text input
    district: str = Form(None),          # Optional district passed from frontend
    crop: str = Form(None)               # Optional target crop selected by user
):
    """
    Handles crop suggestion requests using manual soil details, PDF text extraction,
    or image-based AI analysis.
    """
    enforce_rate_limit(request, "ai_recommendation", max_requests=10, window_seconds=60)

    if not soil_report and not soil_details:
        raise HTTPException(
            status_code=400,
            detail="Either a soil report file or soil details text must be provided.",
        )

    selected_district = (district or current_user.district or "Karnataka").strip()
    analysis_parts: List[str] = []
    image_data_url: Optional[str] = None

    if soil_details and soil_details.strip():
        analysis_parts.append(soil_details.strip())

    if soil_report:
        contents = await soil_report.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded soil report is empty.")
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file exceeds 10MB limit.")

        content_type = soil_report.content_type or "application/octet-stream"

        if content_type == "application/pdf" or soil_report.filename.lower().endswith(".pdf"):
            extracted_text = _extract_pdf_text(contents)
            if not extracted_text:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to extract text from this PDF. Please paste the soil details manually or upload a clearer text-based PDF.",
                )
            analysis_parts.append(f"Extracted soil report text:\n{extracted_text}")
        elif content_type.startswith("image/"):
            image_data_url = _build_image_data_url(content_type, contents)
            analysis_parts.append(
                f"Image soil report uploaded: {soil_report.filename}. Use the image to infer relevant soil indicators."
            )
        else:
            decoded_text = _decode_text_bytes(contents)
            if not decoded_text:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Upload a PDF, image, or a text-based report.",
                )
            analysis_parts.append(f"Uploaded soil report text:\n{decoded_text}")

    if not analysis_parts:
        raise HTTPException(
            status_code=400,
            detail="No usable soil information was found in the request.",
        )

    analysis_parts.append(
        f"Location Context: The soil sample is from {selected_district}, Karnataka, India."
    )
    analysis_input = "\n\n".join(analysis_parts)

    try:
        ai_result = get_crop_suggestion(
            settings.GROQ_API_KEY,
            analysis_input,
            selected_district,
            image_data_url=image_data_url,
            selected_crop=crop,
        )
        _log_ai_history(
            db,
            current_user.id,
            "crop_suggestion",
            {"district": selected_district, "crop": crop or "Auto-recommend", "summary": analysis_input[:500]},
            ai_result,
        )
        return CropRecommendationResponse(**ai_result)
    except ValueError as exc:
        logger.error(f"AI ValueError in crop suggestion: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process AI recommendation due to service error.")
    except RuntimeError as exc:
        logger.error(f"AI RuntimeError in crop suggestion: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process AI recommendation due to runtime error.")
    except Exception as exc:
        logger.error(f"Unexpected error in crop suggestion: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate crop suggestion at this time.",
        )


class FarmerFormData(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None


class LandFormData(BaseModel):
    land_size: Optional[float] = None
    irrigation_type: Optional[str] = None


class SoilFormData(BaseModel):
    soil_type: Optional[str] = None
    soil_depth: Optional[float] = None
    soil_texture: Optional[str] = None


class NutrientFormData(BaseModel):
    ph: float
    ec: Optional[float] = None
    organic_carbon: Optional[float] = None
    nitrogen: float
    phosphorus: float
    potassium: float
    sulphur: Optional[float] = None
    zinc: Optional[float] = None
    iron: Optional[float] = None
    copper: Optional[float] = None
    manganese: Optional[float] = None


class ClimateFormData(BaseModel):
    avg_rainfall: Optional[float] = None
    monsoon_dependent: Optional[bool] = None


class HistoryFormData(BaseModel):
    last_crop: Optional[str] = None


class GoalsFormData(BaseModel):
    season: Optional[str] = None
    purpose: Optional[str] = None
    risk_preference: Optional[str] = None


class StructuredCropRecommendationRequest(BaseModel):
    farmer: Optional[FarmerFormData] = None
    land: Optional[LandFormData] = None
    soil: Optional[SoilFormData] = None
    nutrients: NutrientFormData
    climate: Optional[ClimateFormData] = None
    history: Optional[HistoryFormData] = None
    goals: Optional[GoalsFormData] = None
    target_crop: Optional[str] = None


@router.post("/crop-recommendation-structured", response_model=CropRecommendationResponse)
async def get_structured_crop_recommendation(
    request: Request,
    request_body: StructuredCropRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Handles crop suggestion requests from the structured farm profile form.
    Accepts a JSON payload with farmer, land, soil, nutrients, climate, history, and goals.
    """
    enforce_rate_limit(request, "ai_recommendation_structured", max_requests=10, window_seconds=60)
    errors = []

    # Validate required nutrient fields
    if not is_valid_ph(request_body.nutrients.ph):
        errors.append("Soil pH must be between 0 and 14.")
    if not is_valid_npk(request_body.nutrients.nitrogen):
        errors.append("Nitrogen (N) must be a non-negative number.")
    if not is_valid_npk(request_body.nutrients.phosphorus):
        errors.append("Phosphorus (P) must be a non-negative number.")
    if not is_valid_npk(request_body.nutrients.potassium):
        errors.append("Potassium (K) must be a non-negative number.")

    # Validate optional fields if provided
    if request_body.land and request_body.land.land_size is not None:
        if not is_valid_land_size(request_body.land.land_size):
            errors.append("Land size must be greater than zero.")
    if request_body.land and request_body.land.irrigation_type:
        if not is_valid_irrigation_type(request_body.land.irrigation_type):
            errors.append("Please select a valid irrigation type.")
    if request_body.climate and request_body.climate.avg_rainfall is not None:
        if not is_valid_rainfall(request_body.climate.avg_rainfall):
            errors.append("Rainfall must be a non-negative number.")
    if request_body.soil and request_body.soil.soil_type:
        if not is_valid_soil_type(request_body.soil.soil_type):
            errors.append("Please select a valid soil type.")
    if request_body.soil and request_body.soil.soil_texture:
        if not is_valid_soil_texture(request_body.soil.soil_texture):
            errors.append("Please select a valid soil texture.")
    if request_body.goals and request_body.goals.season:
        if not is_valid_season(request_body.goals.season):
            errors.append("Please select a valid season.")
    if request_body.goals and request_body.goals.purpose:
        if not is_valid_purpose(request_body.goals.purpose):
            errors.append("Please select a valid crop purpose.")
    if request_body.goals and request_body.goals.risk_preference:
        if not is_valid_risk_preference(request_body.goals.risk_preference):
            errors.append("Please select a valid risk preference.")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(errors),
        )

    district = (
        (request_body.farmer.district if request_body.farmer and request_body.farmer.district else None)
        or current_user.district
        or "Karnataka"
    ).strip()

    structured_payload = {
        "farmer": request_body.farmer.model_dump() if request_body.farmer else {},
        "land": request_body.land.model_dump() if request_body.land else {},
        "soil": request_body.soil.model_dump() if request_body.soil else {},
        "nutrients": request_body.nutrients.model_dump(),
        "climate": request_body.climate.model_dump() if request_body.climate else {},
        "history": request_body.history.model_dump() if request_body.history else {},
        "goals": request_body.goals.model_dump() if request_body.goals else {},
    }

    # Add district to land section for the AI context builder
    structured_payload["land"]["district"] = district

    try:
        ai_result = get_structured_crop_suggestion(
            settings.GROQ_API_KEY,
            structured_payload,
            district,
            selected_crop=request_body.target_crop,
        )
        _log_ai_history(
            db,
            current_user.id,
            "crop_suggestion",
            {"district": district, "crop": request_body.target_crop or "Auto-recommend", "structured_payload": structured_payload},
            ai_result,
        )
        return CropRecommendationResponse(**ai_result)
    except ValueError as exc:
        logger.error(f"AI ValueError in structured suggestion: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process AI recommendation due to service error.")
    except RuntimeError as exc:
        logger.error(f"AI RuntimeError in structured suggestion: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process AI recommendation due to runtime error.")
    except Exception as exc:
        logger.error(f"Unexpected error in structured suggestion: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate crop suggestion at this time.",
        )


class CropPlanReminders(BaseModel):
    watering: bool = False
    fertilizing: bool = False
    pest_control: bool = False
    pruning: bool = False


class CropPlanCreateRequest(BaseModel):
    crop: str
    planting_date: date
    purpose: Optional[str] = "Commercial Sale"
    season: Optional[str] = None
    soil_type: Optional[str] = None
    soil_texture: Optional[str] = None
    soil_depth: Optional[float] = None
    soil_ph: Optional[float] = None
    organic_carbon: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ec: Optional[float] = None
    rainfall: Optional[float] = None
    monsoon_dependent: Optional[bool] = True
    previous_crop: Optional[str] = None
    reminders: CropPlanReminders = Field(default_factory=CropPlanReminders)


class CropPlanStageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    title: str
    description: str
    day_range: str
    start_date: str
    end_date: str
    tasks: List[Any]


class CropPlanResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    crop: str
    crop_label: str
    planting_date: str
    harvest_date: str
    duration_days: int
    duration_months: float
    reminders: dict
    stages: List[Any]
    current_stage: Optional[dict] = None
    live_reminder: Optional[dict] = None
    created_at: Optional[str] = None
    is_active: bool


@router.post("/crop-planner", response_model=CropPlanResponse)
async def create_crop_plan(
    request: Request,
    plan_request: CropPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "ai_planner", max_requests=10, window_seconds=60)
    crop_key = plan_request.crop.lower().strip()
    crop_config = get_crop_planner_config(crop_key)
    planting_date = plan_request.planting_date

    season = plan_request.season
    if not season:
        m = planting_date.month
        season = "Kharif" if 6 <= m <= 10 else ("Rabi" if m in [11, 12, 1, 2] else "Summer")

    soil_details = {
        "soil_type": plan_request.soil_type,
        "soil_texture": plan_request.soil_texture,
        "soil_depth": plan_request.soil_depth,
        "soil_ph": plan_request.soil_ph,
        "organic_carbon": plan_request.organic_carbon,
        "nitrogen": plan_request.nitrogen,
        "phosphorus": plan_request.phosphorus,
        "potassium": plan_request.potassium,
        "ec": plan_request.ec,
    }
    climate_details = {
        "rainfall": plan_request.rainfall,
        "monsoon_dependent": plan_request.monsoon_dependent,
    }

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured in settings.")

    try:
        ai_raw_json = generate_ai_crop_plan(
            api_key=api_key,
            farmer_name=current_user.name,
            district=current_user.district or "Karnataka",
            land_size=current_user.land_size or 1.0,
            irrigation_type=current_user.irrigation_type or "Rainfed / Well",
            crop=plan_request.crop,
            start_date=planting_date.isoformat(),
            season=season,
            purpose=plan_request.purpose,
            soil_details=soil_details,
            climate_details=climate_details,
            previous_crop=plan_request.previous_crop,
        )
        ai_plan_data = process_ai_crop_plan(ai_raw_json, planting_date)
    except Exception as exc:
        logger.error(f"AI Crop Plan generation failed: {exc}")
        raise HTTPException(status_code=500, detail="Unable to generate AI crop plan at this time.")

    duration_days = ai_plan_data["estimated_total_duration_days"]
    harvest_date = parse_date_value(ai_plan_data["estimated_harvest_date"])

    crop_plan = CropPlan(
        user_id=current_user.id,
        crop=crop_key,
        planting_date=planting_date,
        harvest_date=harvest_date,
        duration_days=duration_days,
        reminders_json=json.dumps(plan_request.reminders.model_dump()),
        stages_json=json.dumps(ai_plan_data),
    )
    try:
        db.add(crop_plan)
        db.commit()
        db.refresh(crop_plan)
    except Exception as exc:
        db.rollback()
        logger.error(f"Database error saving crop plan: {exc}")
        raise HTTPException(status_code=500, detail="Unable to save crop plan.")

    serialized = serialize_crop_plan(crop_plan)
    _log_ai_history(
        db,
        current_user.id,
        "crop_planner",
        plan_request.model_dump(),
        serialized,
    )
    return CropPlanResponse(**serialized)


@router.post("/crop-planner/regenerate/{plan_id}", response_model=CropPlanResponse)
async def regenerate_crop_plan(
    request: Request,
    plan_id: int,
    plan_request: CropPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, "ai_planner", max_requests=10, window_seconds=60)
    crop_plan = db.query(CropPlan).filter(CropPlan.id == plan_id, CropPlan.user_id == current_user.id).first()
    if not crop_plan:
        raise HTTPException(status_code=404, detail="Crop plan not found.")

    crop_key = plan_request.crop.lower().strip()
    planting_date = plan_request.planting_date

    season = plan_request.season
    if not season:
        m = planting_date.month
        season = "Kharif" if 6 <= m <= 10 else ("Rabi" if m in [11, 12, 1, 2] else "Summer")

    soil_details = {
        "soil_type": plan_request.soil_type,
        "soil_texture": plan_request.soil_texture,
        "soil_depth": plan_request.soil_depth,
        "soil_ph": plan_request.soil_ph,
        "organic_carbon": plan_request.organic_carbon,
        "nitrogen": plan_request.nitrogen,
        "phosphorus": plan_request.phosphorus,
        "potassium": plan_request.potassium,
        "ec": plan_request.ec,
    }
    climate_details = {
        "rainfall": plan_request.rainfall,
        "monsoon_dependent": plan_request.monsoon_dependent,
    }

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured.")

    try:
        ai_raw_json = generate_ai_crop_plan(
            api_key=api_key,
            farmer_name=current_user.name,
            district=current_user.district or "Karnataka",
            land_size=current_user.land_size or 1.0,
            irrigation_type=current_user.irrigation_type or "Rainfed / Well",
            crop=request.crop,
            start_date=planting_date.isoformat(),
            season=season,
            purpose=request.purpose or "Commercial Sale",
            soil_details=soil_details,
            climate_details=climate_details,
            previous_crop=request.previous_crop,
        )
        ai_plan_data = process_ai_crop_plan(ai_raw_json, planting_date)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to regenerate AI crop plan: {exc}")

    try:
        crop_plan.crop = crop_key
        crop_plan.planting_date = planting_date
        crop_plan.duration_days = ai_plan_data["estimated_total_duration_days"]
        crop_plan.harvest_date = parse_date_value(ai_plan_data["estimated_harvest_date"])
        crop_plan.reminders_json = json.dumps(plan_request.reminders.model_dump())
        crop_plan.stages_json = json.dumps(ai_plan_data)
        db.commit()
        db.refresh(crop_plan)
    except Exception as exc:
        db.rollback()
        logger.error(f"Database error updating crop plan: {exc}")
        raise HTTPException(status_code=500, detail="Unable to update crop plan.")

    serialized = serialize_crop_plan(crop_plan)
    _log_ai_history(
        db,
        current_user.id,
        "crop_planner_regenerate",
        plan_request.model_dump(),
        serialized,
    )
    return CropPlanResponse(**serialized)


class InputSuggestionsRequest(BaseModel):
    crop: str
    land_size: float

class InputItem(BaseModel):
    name: str
    quantity: str
    brands: List[str]

class InputSuggestionsResponse(BaseModel):
    seeds: InputItem
    fertilizers: InputItem
    pesticides: InputItem

# ... (existing routes like profile, soil-library, weather, crop-recommendation, etc.) ...

@router.post("/input-suggestions", response_model=InputSuggestionsResponse)
async def get_input_suggestions(
    http_request: Request,
    request: InputSuggestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handles input suggestions request based on crop and land size.
    Returns recommended quantities and brands for seeds, fertilizers, and pesticides.
    """
    enforce_rate_limit(http_request, "ai_suggestions", max_requests=10, window_seconds=60)
    crop = request.crop.strip()
    land_size = request.land_size

    if not crop or len(crop) > 100:
        raise HTTPException(status_code=400, detail="Invalid crop specified.")

    # Validate land size
    if land_size <= 0:
        raise HTTPException(status_code=400, detail="Land size must be greater than zero.")

    factor = land_size

    # Define standard rates per acre (these would ideally come from a DB or external source)
    standard_rates = {
        "rice": {
            "seeds": {
                "rate_per_acre": 25,
                "unit": "kg",
                "brands": ["MTU 1010", "BPT 5204", "IR 64"],
            },
            "fertilizers": {
                "rate_per_acre": 100,
                "unit": "kg",
                "brands": ["IFFCO DAP", "Coromandel NPK 20-20-0", "Urea"],
            },
            "pesticides": {
                "rate_per_acre": 1.5,
                "unit": "liters",
                "brands": ["Bayer Ricestar", "Syngenta Virtako", "FMC Regent"],
            },
        },
        "ragi": {
            "seeds": {
                "rate_per_acre": 8,
                "unit": "kg",
                "brands": ["GPU 28", "ML 365", "KMR 301"],
            },
            "fertilizers": {
                "rate_per_acre": 50,
                "unit": "kg",
                "brands": ["IFFCO 19-19-19", "DAP", "Potash"],
            },
            "pesticides": {
                "rate_per_acre": 0.8,
                "unit": "liters",
                "brands": ["Bayer Confidor", "Syngenta Karate", "UPL Saaf"],
            },
        },
        "maize": {
            "seeds": {
                "rate_per_acre": 8,
                "unit": "kg",
                "brands": ["Pioneer 3396", "NK 6240", "Dekalb 9108"],
            },
            "fertilizers": {
                "rate_per_acre": 90,
                "unit": "kg",
                "brands": ["Urea", "DAP", "MOP"],
            },
            "pesticides": {
                "rate_per_acre": 1.0,
                "unit": "liters",
                "brands": ["Coragen", "Ampligo", "Benevia"],
            },
        },
        "jowar": {
            "seeds": {
                "rate_per_acre": 4,
                "unit": "kg",
                "brands": ["CSV 27", "CSH 16", "M 35-1"],
            },
            "fertilizers": {
                "rate_per_acre": 40,
                "unit": "kg",
                "brands": ["DAP", "Urea", "NPK 14-35-14"],
            },
            "pesticides": {
                "rate_per_acre": 0.8,
                "unit": "liters",
                "brands": ["Chlorpyrifos", "Karate", "Quinalphos"],
            },
        },
        "groundnut": {
            "seeds": {
                "rate_per_acre": 60,
                "unit": "kg",
                "brands": ["JL 24", "TMV 2", "GPBD 4"],
            },
            "fertilizers": {
                "rate_per_acre": 75,
                "unit": "kg",
                "brands": ["Gypsum", "DAP", "SSP"],
            },
            "pesticides": {
                "rate_per_acre": 1.0,
                "unit": "liters",
                "brands": ["Imidacloprid", "Chlorantraniliprole", "Mancozeb"],
            },
        },
        "sugarcane": {
            "seeds": {
                "rate_per_acre": 3500,
                "unit": "sets",
                "brands": ["Co 86032", "CoC 671", "Co 94012"],
            },
            "fertilizers": {
                "rate_per_acre": 150,
                "unit": "kg",
                "brands": ["Urea", "MOP", "DAP"],
            },
            "pesticides": {
                "rate_per_acre": 1.5,
                "unit": "liters",
                "brands": ["Chlorpyrifos", "Fipronil", "Thiamethoxam"],
            },
        },
        "cotton": {
            "seeds": {
                "rate_per_acre": 1.0,
                "unit": "packets",
                "brands": ["RCH 659 BG II", "NCS 145", "Ajeet 155 BG II"],
            },
            "fertilizers": {
                "rate_per_acre": 100,
                "unit": "kg",
                "brands": ["Cotton Special NPK", "Urea", "DAP"],
            },
            "pesticides": {
                "rate_per_acre": 1.2,
                "unit": "liters",
                "brands": ["Emamectin Benzoate", "Profenophos", "Neem Oil"],
            },
        },
        "banana": {
            "seeds": {
                "rate_per_acre": 700,
                "unit": "plants",
                "brands": ["Grand Naine", "Robusta", "Rasthali"],
            },
            "fertilizers": {
                "rate_per_acre": 120,
                "unit": "kg",
                "brands": ["Urea", "MOP", "19-19-19 Water Soluble"],
            },
            "pesticides": {
                "rate_per_acre": 1.5,
                "unit": "liters",
                "brands": ["Monocrotophos", "Imidacloprid", "Propiconazole"],
            },
        },
        "coconut": {
            "seeds": {
                "rate_per_acre": 70,
                "unit": "seedlings",
                "brands": ["Tiptur Tall", "Chowghat Orange Dwarf", "Malayan Green Dwarf"],
            },
            "fertilizers": {
                "rate_per_acre": 175,
                "unit": "kg",
                "brands": ["Coconut Special Mixture", "Urea", "MOP"],
            },
            "pesticides": {
                "rate_per_acre": 1.0,
                "unit": "liters",
                "brands": ["Neem Oil", "Chlorpyrifos", "Hexaconazole"],
            },
        },
        "coffee": {
            "seeds": {
                "rate_per_acre": 600,
                "unit": "saplings",
                "brands": ["Selection 9", "Selection 795", "Chandragiri"],
            },
            "fertilizers": {
                "rate_per_acre": 100,
                "unit": "kg",
                "brands": ["Coffee Special 17-17-17", "Urea", "Rock Phosphate"],
            },
            "pesticides": {
                "rate_per_acre": 1.0,
                "unit": "liters",
                "brands": ["Bordeaux Mixture", "Chlorpyrifos", "Copper Oxychloride"],
            },
        },
        "tomato": {
            "seeds": {
                "rate_per_acre": 0.1,
                "unit": "kg",
                "brands": ["Arka Rakshak", "Arka Samrat", "NS 4266"],
            },
            "fertilizers": {
                "rate_per_acre": 90,
                "unit": "kg",
                "brands": ["Calcium Nitrate", "19-19-19", "MOP"],
            },
            "pesticides": {
                "rate_per_acre": 1.0,
                "unit": "liters",
                "brands": ["Actara", "Tracer", "Ridomil Gold"],
            },
        },
    }

    crop_info = standard_rates.get(crop.split("(")[0].strip().lower()) or standard_rates.get(crop.lower()) or {"seeds": {"rate_per_acre": 8, "unit": "kg/plants", "brands": ["Improved Hybrid", "MAHYCO", "Namdhari"]}, "fertilizers": {"rate_per_acre": 75, "unit": "kg", "brands": ["IFFCO DAP", "Urea", "NPK 19-19-19"]}, "pesticides": {"rate_per_acre": 1.0, "unit": "liters", "brands": ["Bayer CropScience", "Syngenta", "UPL"]}}
    if not crop_info:
        raise HTTPException(
            status_code=400,
            detail=f"No input suggestion data configured for crop: {crop}.",
        )

    # Calculate quantities
    seeds_quantity = round(crop_info["seeds"]["rate_per_acre"] * factor, 1)
    fertilizers_quantity = round(crop_info["fertilizers"]["rate_per_acre"] * factor, 1)
    pesticides_quantity = round(crop_info["pesticides"]["rate_per_acre"] * factor, 1)

    # Construct the response
    response_data = InputSuggestionsResponse(
        seeds=InputItem(
            name=f"{crop.capitalize()} Seeds",
            quantity=f"{seeds_quantity} {crop_info['seeds']['unit']}",
            brands=crop_info["seeds"]["brands"]
        ),
        fertilizers=InputItem(
            name="Fertilizer",
            quantity=f"{fertilizers_quantity} {crop_info['fertilizers']['unit']}",
            brands=crop_info["fertilizers"]["brands"]
        ),
        pesticides=InputItem(
            name="Pesticide",
            quantity=f"{pesticides_quantity} {crop_info['pesticides']['unit']}",
            brands=crop_info["pesticides"]["brands"]
        )
    )

    _log_ai_history(
        db,
        current_user.id,
        "input_suggestions",
        request.model_dump(),
        response_data.model_dump(),
    )
    return response_data


class DiseaseDiagnosisRequest(BaseModel):
    symptoms_description: str
    district: str

class DiseaseDiagnosisResponse(BaseModel):
    diagnosis: str
    symptoms: str
    treatment: str
    prevention: str

# ... (existing routes like profile, soil-library, weather, crop-recommendation, input-suggestions, etc.) ...

@router.post("/disease-diagnosis", response_model=DiseaseDiagnosisResponse)
async def get_disease_diagnosis(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    plant_image: UploadFile = File(None), # Optional image upload
    symptoms_description: Optional[str] = Form(None),
    district: str = Form(None)           # Optional district passed from frontend
):
    """
    Handles disease diagnosis request.
    Accepts an optional plant image and/or symptom description.
    Calls the Groq AI API to analyze the data and diagnose the disease.
    """
    enforce_rate_limit(request, "ai_diagnosis", max_requests=10, window_seconds=60)
    symptoms_description = (symptoms_description or "").strip()
    selected_district = (district or current_user.district or "Karnataka").strip()
    image_data_url: Optional[str] = None

    if plant_image:
        content_type = (plant_image.content_type or "").lower()
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Plant image must be a JPG, PNG, WEBP, or another valid image format.",
            )

        contents = await plant_image.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded plant image is empty.")
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded image exceeds 10MB limit.")

        image_data_url = _build_image_data_url(content_type, contents)

    if not symptoms_description and not image_data_url:
        raise HTTPException(
            status_code=400,
            detail="Provide either symptoms description or a plant image.",
        )

    try:
        ai_result = generate_disease_diagnosis(
            settings.GROQ_API_KEY,
            symptoms_description,
            selected_district,
            image_data_url=image_data_url,
        )
        _log_ai_history(
            db,
            current_user.id,
            "disease_diagnosis",
            {"district": selected_district, "symptoms": symptoms_description, "has_image": bool(image_data_url)},
            ai_result,
        )
        return DiseaseDiagnosisResponse(**ai_result)
    except ValueError as exc:
        logger.error(f"AI ValueError in disease diagnosis: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process disease diagnosis due to service error.")
    except RuntimeError as exc:
        logger.error(f"AI RuntimeError in disease diagnosis: {exc}")
        raise HTTPException(status_code=502, detail="Unable to process disease diagnosis due to runtime error.")
    except Exception as exc:
        logger.error(f"Unexpected error in disease diagnosis: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate disease diagnosis at this time.",
        )


# backend/routes/user.py

# ... (other imports) ...



class MarketPriceItem(BaseModel):
    id: int
    crop_name: str
    variety: Optional[str] = None
    grade: Optional[str] = None
    district: str
    mandi_name: str
    arrival: Optional[float] = None
    unit: Optional[str] = None
    price_per_quintal: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_date: date
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

# ... (existing routes like profile, soil-library, weather, crop-recommendation, input-suggestions, disease-diagnosis, crop-planner, etc.) ...

@router.get("/market-prices", response_model=List[MarketPriceItem])
async def get_market_prices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches the latest imported Karnataka mandi snapshot from the database.
    """
    current_rows = (
        db.query(Price)
        .order_by(Price.crop_name.asc(), Price.district.asc(), Price.mandi_name.asc())
        .all()
    )

    return [
        MarketPriceItem(
            id=row.id,
            crop_name=row.crop_name,
            variety=row.variety,
            grade=row.grade,
            district=row.district,
            mandi_name=row.mandi_name,
            arrival=row.arrival,
            unit=row.unit,
            price_per_quintal=row.price_per_quintal,
            min_price=row.min_price,
            max_price=row.max_price,
            price_date=row.price_date,
            last_updated=row.last_updated,
            created_at=row.created_at,
        )
        for row in current_rows
    ]

# backend/routes/user.py

# ... (other imports) ...



# Define a Pydantic model for a government scheme
class GovScheme(BaseModel):
    id: int
    title: str
    description: str
    type: str
    beneficiary: Optional[str] = None
    benefits: str
    eligibility: str
    documents_required: List[str]
    steps_to_apply: List[str]
    duration: Optional[str] = None
    official_link: str
    icon: Optional[str] = "fas fa-hand-holding-heart"
    state: Optional[str] = None
    district: Optional[str] = None
    is_active: bool = True

# ... (existing routes like profile, soil-library, weather, crop-recommendation, input-suggestions, disease-diagnosis, crop-planner, mandi-tracking, etc.) ...

@router.get("/gov-schemes-data", response_model=List[GovScheme])
async def get_government_schemes(
    scheme_type: Optional[str] = None,
    beneficiary: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches active national and Karnataka-relevant schemes from the database.
    """
    user_state = (current_user.state or "").strip()
    user_district = (current_user.district or "").strip()

    schemes = [
        scheme_to_payload(scheme)
        for scheme in db.query(Scheme)
        .filter(Scheme.is_active == True)
        .order_by(Scheme.type.asc(), Scheme.title.asc())
        .all()
    ]

    schemes = [
        scheme for scheme in schemes
        if scheme["type"] == "national"
        or (
            scheme["type"] == "state"
            and (
                not scheme.get("state")
                or scheme.get("state") == "Karnataka"
                or scheme.get("state") == user_state
            )
        )
    ]

    if scheme_type:
        schemes = [scheme for scheme in schemes if scheme["type"] == scheme_type]

    if beneficiary:
        beneficiary_value = beneficiary.lower()
        schemes = [
            scheme for scheme in schemes
            if (scheme.get("beneficiary") or "").lower() == beneficiary_value
            or beneficiary_value in (scheme.get("eligibility") or "").lower()
        ]

    if search:
        search_value = search.lower()
        schemes = [
            scheme for scheme in schemes
            if search_value in (scheme.get("title") or "").lower()
            or search_value in (scheme.get("description") or "").lower()
            or search_value in (scheme.get("benefits") or "").lower()
            or search_value in (scheme.get("eligibility") or "").lower()
        ]

    if user_district:
        schemes = [
            scheme for scheme in schemes
            if not scheme.get("district") or scheme.get("district", "").lower() == user_district.lower()
        ]

    return schemes


    # schemes_from_db = db.query(GovernmentScheme).all() # Assuming you have a GovernmentScheme model
    # return [GovScheme.from_orm(s) for s in schemes_from_db]

    # For now, return mock data matching the GovScheme model structure
    _unused_mock_schemes = [
        GovScheme(
            id=1,
            title="PM Kisan Samman Nidhi",
            description="Income support of ₹6,000 per year to small and marginal farmer families.",
            type="central",
            benefits="₹6,000/year",
            eligibility="≤2 hectares",
            documents_required=["Land records", "Aadhaar card", "Bank account details"],
            steps_to_apply=[
                "Register on PM Kisan portal",
                "Verify Aadhaar",
                "Link bank account",
                "Receive direct benefit transfer"
            ],
            duration="Ongoing",
            official_link="https://pmkisan.gov.in/",
            icon="fas fa-rupee-sign"
        ),
        GovScheme(
            id=2,
            title="PM Fasal Bima Yojana",
            description="Crop insurance scheme to provide financial support to farmers in case of crop loss.",
            type="central",
            benefits="Insurance coverage",
            eligibility="All farmers growing notified crops",
            documents_required=["Seed purchase receipt", "Land ownership proof", "Photo of crop"],
            steps_to_apply=[
                "Enroll through Common Service Centers (CSCs) or online",
                "Pay premium (1.5-5% of sum insured)",
                "Submit claim post-loss",
                "Receive compensation"
            ],
            duration="Ongoing",
            official_link="https://pmfby.gov.in/",
            icon="fas fa-shield-alt"
        ),
        GovScheme(
            id=3,
            title="National Agriculture Market",
            description="Online trading platform to connect farmers with buyers across states.",
            type="central",
            benefits="Better prices",
            eligibility="Registered farmers and traders",
            documents_required=["Aadhaar card", "Bank account", "Produce samples"],
            steps_to_apply=[
                "Register on e-NAM portal",
                "Create farmer account",
                "List produce for auction",
                "Sell to highest bidder"
            ],
            duration="Ongoing",
            official_link="https://e-nam.gov.in/",
            icon="fas fa-store"
        ),
        # Add more mock schemes or fetch from DB as needed
        # Example for a state scheme
        GovScheme(
            id=4,
            title="Karnataka State Agricultural Support",
            description="Subsidies for modern farming equipment and techniques.",
            type="state",
            benefits="Up to 50% subsidy",
            eligibility="Farmers in Karnataka",
            documents_required=["Land records", "Income certificate", "Equipment invoice"],
            steps_to_apply=[
                "Apply through Karnataka Agriculture Department portal",
                "Submit required documents",
                "Attend verification",
                "Receive subsidy after purchase"
            ],
            duration="Annual application cycle",
            official_link="https://krishimaratavani.karnataka.gov.in/",
            icon="fas fa-seedling"
        )
    ]


# ... (rest of existing routes) ...
