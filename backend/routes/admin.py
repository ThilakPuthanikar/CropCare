# backend/routes/admin.py

import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func # Import for aggregation functions like COUNT, SUM, etc.
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional # Import for type hints
from pydantic import BaseModel

from ..database.database import get_db
from ..models.user import User
from ..models.ad import Ad
from ..models.scheme import Scheme
from ..models.price import Price # Assuming you created this model
from ..schemas.user import UserInDB, UserUpdate # Assuming you have these schemas
from ..schemas.ad import AdCreate, AdUpdate, AdInDB # Assuming you have these schemas
from ..schemas.scheme import SchemeCreate, SchemeUpdate, SchemeInDB # Assuming you have these schemas
from ..schemas.price import PriceCreate, PriceUpdate, PriceInDB # Assuming you have these schemas
from ..services.mandi_service import KARNATAKA_MANDI_SOURCE_URL, fetch_karnataka_mandi_prices
from ..utils.schemes import scheme_to_payload, serialize_text_list
from ..utils.auth import get_current_admin

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


class MandiPreviewItem(BaseModel):
    crop_name: str
    variety: Optional[str] = None
    grade: Optional[str] = None
    district: str
    mandi_name: str
    arrival: Optional[float] = None
    unit: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_per_quintal: float
    price_date: date
    last_updated: Optional[datetime] = None


class MandiFetchResponse(BaseModel):
    source_url: str
    fetched_at: datetime
    row_count: int
    records: List[MandiPreviewItem]


class MandiImportRequest(BaseModel):
    records: List[MandiPreviewItem]


class MandiImportResponse(BaseModel):
    status: str
    inserted_rows: int
    imported_at: datetime


def _summary_stats(db: Session):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_approved == True).count()
    pending_approval = db.query(User).filter(User.is_approved == False).count()
    ai_requests = 156
    return {
        "total_users": total_users,
        "active_users": active_users,
        "pending_approval": pending_approval,
        "ai_requests": ai_requests
    }

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    stats = _summary_stats(db)

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": current_user,
        **stats
    })


@router.get("/stats")
async def get_dashboard_stats(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return _summary_stats(db)


@router.get("/recent-activities")
async def get_recent_activities(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).limit(8).all()
    activities = []
    now = datetime.now(timezone.utc)

    for user in users:
        created_at = user.created_at or now
        if getattr(created_at, "tzinfo", None) is not None and getattr(now, "tzinfo", None) is None:
            now_for_user = datetime.now(created_at.tzinfo)
        else:
            now_for_user = now
        delta = now_for_user - created_at
        if delta.days > 0:
            time_ago = f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            time_ago = f"{delta.seconds // 3600}h ago"
        else:
            time_ago = f"{max(1, delta.seconds // 60)}m ago"

        activities.append({
            "type": "user_approved" if user.is_approved else "user_registered",
            "action": "User approved" if user.is_approved else "User registered",
            "details": f"{user.name} ({user.email})",
            "time_ago": time_ago
        })

    return activities

@router.get("/manage-users", response_class=HTMLResponse)
async def manage_users(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return templates.TemplateResponse("admin/manage_users.html", {
        "request": request,
        "user": current_user,
        "users": users
    })

@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {"name", "phone_number", "district", "land_size", "irrigation_type", "role", "is_approved"}
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to update user details.")

@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_approved:
        return {"message": "User is already approved"}

    user.is_approved = True
    try:
        db.commit()
        return {"message": "User approved successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error approving user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to approve user.")

@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_approved = False
    try:
        db.commit()
        return {"message": "User rejected successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error rejecting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to reject user.")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete user.")

# --- AD ROUTES ---
@router.get("/manage-ads", response_class=HTMLResponse)
async def manage_ads(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ads = db.query(Ad).all()
    return templates.TemplateResponse("admin/manage_ads.html", {
        "request": request,
        "user": current_user,
        "ads": ads
    })

@router.get("/ads", response_model=List[AdInDB])
async def get_ads(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ads = db.query(Ad).all()
    return ads

@router.post("/ads", response_model=AdInDB)
async def create_ad(
    ad_create: AdCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_ad = Ad(**ad_create.dict())
    try:
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)
        return new_ad
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating ad: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during ad creation.")

@router.get("/ads/{ad_id}", response_model=AdInDB)
async def get_ad(
    ad_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@router.put("/ads/{ad_id}", response_model=AdInDB)
async def update_ad(
    ad_id: int,
    ad_update: AdUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    update_data = ad_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)

    try:
        db.commit()
        db.refresh(ad)
        return ad
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating ad {ad_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during ad update.")

@router.delete("/ads/{ad_id}")
async def delete_ad(
    ad_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    try:
        db.delete(ad)
        db.commit()
        return {"message": "Ad deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting ad {ad_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during ad deletion.")

# --- SCHEME ROUTES ---
@router.get("/manage-schemes", response_class=HTMLResponse)
async def manage_schemes(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    schemes = db.query(Scheme).all()
    return templates.TemplateResponse("admin/manage_schemes.html", {
        "request": request,
        "user": current_user,
        "schemes": schemes
    })

@router.get("/schemes", response_model=List[SchemeInDB])
async def get_schemes(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    schemes = db.query(Scheme).all()
    return [scheme_to_payload(scheme) for scheme in schemes]

@router.post("/schemes", response_model=SchemeInDB)
async def create_scheme(
    scheme_create: SchemeCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    scheme_data = scheme_create.dict()
    scheme_data["documents_required"] = serialize_text_list(scheme_data.get("documents_required"))
    scheme_data["steps_to_apply"] = serialize_text_list(scheme_data.get("steps_to_apply"))
    new_scheme = Scheme(**scheme_data)
    try:
        db.add(new_scheme)
        db.commit()
        db.refresh(new_scheme)
        return scheme_to_payload(new_scheme)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating scheme: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during scheme creation.")

@router.get("/schemes/{scheme_id}", response_model=SchemeInDB)
async def get_scheme(
    scheme_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme_to_payload(scheme)

@router.put("/schemes/{scheme_id}", response_model=SchemeInDB)
async def update_scheme(
    scheme_id: int,
    scheme_update: SchemeUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    update_data = scheme_update.dict(exclude_unset=True)
    if "documents_required" in update_data:
        update_data["documents_required"] = serialize_text_list(update_data["documents_required"])
    if "steps_to_apply" in update_data:
        update_data["steps_to_apply"] = serialize_text_list(update_data["steps_to_apply"])
    for field, value in update_data.items():
        setattr(scheme, field, value)

    try:
        db.commit()
        db.refresh(scheme)
        return scheme_to_payload(scheme)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating scheme {scheme_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during scheme update.")

@router.delete("/schemes/{scheme_id}")
async def delete_scheme(
    scheme_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    try:
        db.delete(scheme)
        db.commit()
        return {"message": "Scheme deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting scheme {scheme_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during scheme deletion.")

# --- PRICE ROUTES ---
@router.get("/manage-prices", response_class=HTMLResponse)
async def manage_prices(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_records = db.query(func.count(Price.id)).scalar() or 0
    district_count = db.query(func.count(func.distinct(Price.district))).scalar() or 0
    market_count = db.query(func.count(func.distinct(Price.mandi_name))).scalar() or 0
    latest_import = db.query(func.max(Price.created_at)).scalar()
    return templates.TemplateResponse("admin/manage_prices.html", {
        "request": request,
        "user": current_user,
        "total_records": total_records,
        "district_count": district_count,
        "market_count": market_count,
        "latest_import": latest_import,
        "source_url": KARNATAKA_MANDI_SOURCE_URL,
    })


@router.post("/mandi/fetch", response_model=MandiFetchResponse)
async def fetch_mandi_prices(
    current_user = Depends(get_current_admin),
):
    try:
        fetched = fetch_karnataka_mandi_prices()
        return MandiFetchResponse(**fetched)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch Karnataka mandi prices: {exc}") from exc


@router.post("/mandi/import", response_model=MandiImportResponse)
async def import_mandi_prices(
    payload: MandiImportRequest,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not payload.records:
        raise HTTPException(status_code=400, detail="No preview records were provided for import.")

    imported_at = datetime.now(timezone.utc)
    logger.info("Import started for Karnataka mandi snapshot")

    try:
        db.query(Price).delete()
        new_rows = []
        for record in payload.records:
            new_rows.append(
                Price(
                    crop_name=record.crop_name,
                    variety=record.variety,
                    grade=record.grade,
                    district=(record.district or "Unknown").strip() or "Unknown",
                    mandi_name=record.mandi_name,
                    arrival=record.arrival,
                    unit=record.unit,
                    price_per_quintal=record.price_per_quintal,
                    min_price=record.min_price,
                    max_price=record.max_price,
                    price_date=record.price_date,
                    last_updated=record.last_updated or imported_at,
                    created_at=imported_at,
                )
            )

        db.add_all(new_rows)
        db.commit()
        logger.info("Records inserted: %s", len(new_rows))
        logger.info("Import completed for Karnataka mandi snapshot")
        return MandiImportResponse(
            status="success",
            inserted_rows=len(new_rows),
            imported_at=imported_at,
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Karnataka mandi import failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to import mandi prices: {exc}") from exc

@router.get("/prices", response_model=List[PriceInDB])
async def get_prices(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    prices = db.query(Price).order_by(Price.price_date.desc(), Price.district.asc(), Price.crop_name.asc()).all()
    return prices

@router.post("/prices", response_model=PriceInDB)
async def create_price(
    price_create: PriceCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing_price = (
        db.query(Price)
        .filter(
            Price.crop_name == price_create.crop_name,
            Price.district == price_create.district,
            Price.mandi_name == price_create.mandi_name,
            Price.price_date == price_create.price_date,
        )
        .first()
    )
    try:
        if existing_price:
            existing_price.price_per_quintal = price_create.price_per_quintal
            existing_price.min_price = price_create.min_price
            existing_price.max_price = price_create.max_price
            existing_price.last_updated = price_create.last_updated
            db.commit()
            db.refresh(existing_price)
            return existing_price

        new_price = Price(**price_create.dict())
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        return new_price
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating price: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during price creation.")

@router.get("/prices/{price_id}", response_model=PriceInDB)
async def get_price(
    price_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price record not found")
    return price

@router.put("/prices/{price_id}", response_model=PriceInDB)
async def update_price(
    price_id: int,
    price_update: PriceUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price record not found")

    update_data = price_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price, field, value)

    try:
        db.commit()
        db.refresh(price)
        return price
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating price {price_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during price update.")

@router.delete("/prices/{price_id}")
async def delete_price(
    price_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price record not found")

    try:
        db.delete(price)
        db.commit()
        return {"message": "Price record deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting price {price_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during price deletion.")

@router.get("/prices/history", response_model=List[PriceInDB])
async def get_price_history(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    recent_prices = db.query(Price).order_by(Price.price_date.desc(), Price.updated_at.desc()).limit(20).all()
    return recent_prices

# --- ANALYTICS ROUTES ---
@router.get("/analytics", response_class=HTMLResponse)
async def analytics(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("admin/analytics.html", {
        "request": request,
        "user": current_user
    })

@router.get("/analytics/summary")
async def get_analytics_summary(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return _summary_stats(db)

@router.get("/analytics/user-growth")
async def get_user_growth(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=6 * 30)
    users_per_month = db.query(
        func.date_format(User.created_at, '%Y-%m').label('month_key'),
        func.count(User.id).label('new_users')
    ).filter(
        User.created_at >= six_months_ago
    ).group_by('month_key').order_by('month_key').all()

    labels = []
    data = []
    for month_data in users_per_month:
        month_key = month_data.month_key
        try:
            label = datetime.strptime(month_key, "%Y-%m").strftime("%b")
        except Exception:
            label = month_key
        labels.append(label)
        data.append(month_data.new_users)

    return {"labels": labels, "data": data}

@router.get("/analytics/ai-usage")
async def get_ai_usage_distribution(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Example: Assume you have a table tracking AI requests with types
    # ai_types = db.query(AIRequestLog.type, func.count(AIRequestLog.id)).group_by(AIRequestLog.type).all()
    # For now, return mock data
    labels = ["Crop Recommendation", "Disease Diagnosis", "Input Suggestions", "Weather Analysis"]
    # Example counts, replace with real aggregated data if available
    data = [42, 28, 20, 10]

    return {"labels": labels, "data": data}

@router.get("/analytics/crop-activity")
async def get_crop_activity(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Example: Aggregate based on some activity log related to crops
    # This could be based on crop recommendation requests, disease diagnoses, etc.
    # For now, return mock data
    labels = ["Rice", "Wheat", "Tomato", "Sugarcane", "Groundnut", "Coffee"]
    # Example counts, replace with real aggregated data
    data = [312, 234, 189, 156, 123, 98]

    return {"labels": labels, "data": data}

@router.get("/analytics/top-crops")
async def get_top_crops_analyzed(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Example: Get top crops based on some analysis activity (e.g., recommendation requests)
    # This requires a table linking analyses to crops
    # For now, return mock data with percentages
    # Example: [{'crop': 'Rice', 'percentage': 42}, {'crop': 'Wheat', 'percentage': 28}, ...]
    top_crops = [
        {"crop": "Rice", "percentage": 42},
        {"crop": "Wheat", "percentage": 28},
        {"crop": "Tomato", "percentage": 18},
        {"crop": "Other", "percentage": 12}
    ]
    return top_crops

@router.get("/analytics/district-distribution")
async def get_district_distribution(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Get user count per district
    district_counts = db.query(
        User.district,
        func.count(User.id).label('user_count')
    ).filter(
        User.district.isnot(None) # Exclude users without a district set
    ).group_by(User.district).all()

    total_users_with_district = sum(count.user_count for count in district_counts)

    if total_users_with_district == 0:
        return [] # Return empty list if no users have district set

    district_data = []
    other_percentage = 0
    for i, dist_count in enumerate(district_counts):
        percentage = round((dist_count.user_count / total_users_with_district) * 100, 2)
        # For demo purposes, limit displayed districts and group others as "Other"
        if i < 4: # Show top 4 districts
            district_data.append({"district": dist_count.district, "percentage": percentage})
        else:
            other_percentage += percentage

    if other_percentage > 0:
        district_data.append({"district": "Other", "percentage": round(other_percentage, 2)})

    return district_data
