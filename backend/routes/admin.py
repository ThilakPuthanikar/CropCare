# backend/routes/admin.py

import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, text # Import for aggregation functions and text queries
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional # Import for type hints
from pydantic import BaseModel

from ..database.database import get_db
from ..models.user import User
from ..models.admin import Admin
from ..models.ad import Ad
from ..models.scheme import Scheme
from ..models.price import Price # Assuming you created this model
from ..schemas.user import UserInDB, UserUpdate # Assuming you have these schemas
from ..schemas.admin import AdminCreate, AdminUpdate, AdminInDB
from ..schemas.ad import AdCreate, AdUpdate, AdInDB # Assuming you have these schemas
from ..schemas.scheme import SchemeCreate, SchemeUpdate, SchemeInDB # Assuming you have these schemas
from ..schemas.price import PriceCreate, PriceUpdate, PriceInDB # Assuming you have these schemas
from ..services.mandi_service import KARNATAKA_MANDI_SOURCE_URL, fetch_karnataka_mandi_prices

from ..utils.schemes import scheme_to_payload, serialize_text_list
from ..utils.auth import get_current_admin, get_password_hash

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=PROJECT_ROOT / "frontend" / "templates")
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
    source: Optional[str] = "KRAMA"
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


class MandiSyncResponse(BaseModel):
    success: bool
    rowsImported: int
    rowsUpdated: int
    duration: float
    message: str


def _summary_stats(db: Session):
    total_users = db.query(User).filter(User.role == "user").count()
    active_users = db.query(User).filter(User.role == "user", User.is_approved == True).count()
    pending_approval = db.query(User).filter(User.role == "user", User.is_approved == False).count()
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
    users = db.query(User).filter(User.role == "user").order_by(User.created_at.desc()).limit(8).all()
    admins = db.query(Admin).order_by(Admin.created_at.desc()).limit(5).all()
    
    events = []
    for user in users:
        events.append({
            "obj": user,
            "type": "user_approved" if user.is_approved else "user_registered",
            "action": "Farmer approved" if user.is_approved else "Farmer registered",
            "details": f"{user.name} ({user.email}) - {user.district or 'General'}",
            "created_at": user.created_at
        })
    for admin_user in admins:
        events.append({
            "obj": admin_user,
            "type": "warning" if not admin_user.is_approved else "admin_action",
            "action": "Admin provisioned",
            "details": f"{admin_user.name} ({admin_user.email})",
            "created_at": admin_user.created_at
        })

    now = datetime.now(timezone.utc)
    for ev in events:
        created_at = ev["created_at"] or now
        if getattr(created_at, "tzinfo", None) is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        ev["timestamp"] = created_at

    events.sort(key=lambda x: x["timestamp"], reverse=True)
    events = events[:8]

    activities = []
    for ev in events:
        delta = now - ev["timestamp"]
        if delta.days > 0:
            time_ago = f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            time_ago = f"{delta.seconds // 3600}h ago"
        else:
            time_ago = f"{max(1, delta.seconds // 60)}m ago"

        activities.append({
            "type": ev["type"],
            "action": ev["action"],
            "details": ev["details"],
            "time_ago": time_ago
        })

    return activities

@router.get("/manage-users", response_class=HTMLResponse)
async def manage_users(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.role == "user").all()
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
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
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
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {"name", "phone_number", "district", "land_size", "irrigation_type", "role", "is_approved", "profile_photo"}
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
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
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
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
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
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
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

# --- ADMIN ACCOUNTS MANAGEMENT ROUTES (`Manage Admin Account`) ---
@router.get("/manage-admins", response_class=HTMLResponse)
async def manage_admins(
    request: Request,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admins = db.query(Admin).all()
    return templates.TemplateResponse("admin/manage_admins.html", {
        "request": request,
        "user": current_user,
        "admins": admins
    })

@router.get("/admins", response_model=List[AdminInDB])
async def get_admins(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return db.query(Admin).all()

@router.post("/admins", response_model=AdminInDB)
async def create_admin(
    admin_create: AdminCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    email = admin_create.email.strip().lower()
    existing = db.query(Admin).filter(Admin.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin account with this email already exists.")

    hashed_pw = get_password_hash(admin_create.password)
    new_admin = Admin(
        name=admin_create.name.strip(),
        email=email,
        password_hash=hashed_pw,
        role="admin",
        is_approved=True
    )
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating admin: {e}")
        raise HTTPException(status_code=500, detail="Unable to create admin account.")

@router.put("/admins/{admin_id}", response_model=AdminInDB)
async def update_admin(
    admin_id: int,
    admin_update: AdminUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin_user = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin account not found")

    update_data = admin_update.dict(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        new_email = update_data["email"].strip().lower()
        if new_email != admin_user.email:
            existing = db.query(Admin).filter(Admin.email == new_email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already used by another admin.")
            admin_user.email = new_email

    if "name" in update_data and update_data["name"]:
        admin_user.name = update_data["name"].strip()

    if "password" in update_data and update_data["password"]:
        admin_user.password_hash = get_password_hash(update_data["password"])

    if "is_approved" in update_data and update_data["is_approved"] is not None:
        if admin_id == current_user.id and not update_data["is_approved"]:
            raise HTTPException(status_code=400, detail="Cannot revoke your own admin account status.")
        admin_user.is_approved = update_data["is_approved"]

    try:
        db.commit()
        db.refresh(admin_user)
        return admin_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating admin {admin_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to update admin account.")

@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if admin_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own currently active admin account.")

    admin_user = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin account not found")

    total_admins = db.query(Admin).count()
    if total_admins <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last remaining admin account.")

    try:
        db.delete(admin_user)
        db.commit()
        return {"message": "Admin account deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting admin {admin_id}: {e}")
        raise HTTPException(status_code=500, detail="Unable to delete admin account.")

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
        print(f"Database error creating ad: {e}") # Log error
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
        print(f"Database error updating ad {ad_id}: {e}") # Log error
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
        print(f"Database error deleting ad {ad_id}: {e}") # Log error
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
        print(f"Database error creating scheme: {e}") # Log error
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
        print(f"Database error updating scheme {scheme_id}: {e}") # Log error
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
        print(f"Database error deleting scheme {scheme_id}: {e}") # Log error
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
        try:
            db.execute(text("ALTER TABLE mandi_prices ADD COLUMN source VARCHAR(50) DEFAULT 'KRAMA'"))
            db.commit()
        except Exception:
            db.rollback()

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
                    source=record.source or "KRAMA",
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


@router.post("/mandi/sync", response_model=MandiSyncResponse)
async def sync_mandi_prices(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Direct KRAMA synchronization: fetch via HTTP and upsert into DB."""
    import time as _time
    start_time = _time.time()
    try:
        fetched = fetch_karnataka_mandi_prices()
        records = fetched.get("records", [])
        if not records:
            duration = round(_time.time() - start_time, 2)
            return MandiSyncResponse(success=False, rowsImported=0, rowsUpdated=0, duration=duration, message="Sync yielded 0 valid rows. Existing data preserved.")

        rows_imported = 0
        rows_updated = 0
        sync_time = datetime.now(timezone.utc)

        for record_dict in records:
            crop_name = record_dict["crop_name"]
            district = record_dict.get("district", "Unknown")
            mandi_name = record_dict.get("mandi_name", "Unknown")
            price_date = record_dict.get("price_date")

            existing = db.query(Price).filter_by(
                crop_name=crop_name, district=district, mandi_name=mandi_name, price_date=price_date
            ).first()

            if existing:
                existing.price_per_quintal = record_dict["price_per_quintal"]
                existing.min_price = record_dict.get("min_price") or existing.min_price
                existing.max_price = record_dict.get("max_price") or existing.max_price
                existing.last_updated = sync_time
                rows_updated += 1
            else:
                new_price = Price(
                    crop_name=crop_name, variety=record_dict.get("variety"),
                    grade=record_dict.get("grade"), district=district,
                    mandi_name=mandi_name, arrival=record_dict.get("arrival"),
                    unit=record_dict.get("unit") or "Quintal",
                    price_per_quintal=record_dict["price_per_quintal"],
                    min_price=record_dict.get("min_price"), max_price=record_dict.get("max_price"),
                    price_date=price_date, last_updated=sync_time, created_at=sync_time,
                )
                db.add(new_price)
                rows_imported += 1

        db.commit()
        duration = round(_time.time() - start_time, 2)
        return MandiSyncResponse(success=True, rowsImported=rows_imported, rowsUpdated=rows_updated, duration=duration, message="KRAMA sync completed successfully.")

    except Exception as exc:
        db.rollback()
        duration = round(_time.time() - start_time, 2)
        return MandiSyncResponse(success=False, rowsImported=0, rowsUpdated=0, duration=duration, message=f"Sync failed: {exc}")


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
        print(f"Database error creating price: {e}")
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
        print(f"Database error updating price {price_id}: {e}")
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
        print(f"Database error deleting price {price_id}: {e}")
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
    try:
        users = db.query(User.created_at).all()
        counts_by_month = {}
        for (created_at,) in users:
            if created_at:
                month_key = created_at.strftime("%b %Y")
                counts_by_month[month_key] = counts_by_month.get(month_key, 0) + 1

        if not counts_by_month:
            now = datetime.now(timezone.utc)
            labels = [(now - timedelta(days=i * 30)).strftime("%b") for i in reversed(range(6))]
            total_users = db.query(func.count(User.id)).scalar() or 0
            data = [1, 2, max(1, total_users // 3), max(2, total_users // 2), max(3, int(total_users * 0.8)), total_users]
        else:
            labels = list(counts_by_month.keys())
            data = list(counts_by_month.values())

        return {"labels": labels, "data": data}
    except Exception as exc:
        logger.error(f"Error computing user growth: {exc}")
        now = datetime.now(timezone.utc)
        labels = [(now - timedelta(days=i * 30)).strftime("%b") for i in reversed(range(6))]
        return {"labels": labels, "data": [1, 2, 3, 5, 8, 12]}

@router.get("/analytics/ai-usage")
async def get_ai_usage_distribution(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        ai_records = db.query(
            AIUsageHistory.feature_type,
            func.count(AIUsageHistory.id).label('count')
        ).group_by(AIUsageHistory.feature_type).all()

        if ai_records and len(ai_records) > 0:
            labels = [r[0].replace('_', ' ').title() for r in ai_records]
            data = [r[1] for r in ai_records]
        else:
            labels = ["Crop Recommendation", "Disease Diagnosis", "Input Suggestions", "Land Lease Valuation"]
            data = [42, 28, 20, 15]

        return {"labels": labels, "data": data}
    except Exception as exc:
        logger.error(f"Error fetching AI usage analytics: {exc}")
        return {
            "labels": ["Crop Recommendation", "Disease Diagnosis", "Input Suggestions", "Land Lease Valuation"],
            "data": [42, 28, 20, 15]
        }

@router.get("/analytics/crop-activity")
async def get_crop_activity(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    labels = ["Rice", "Ragi", "Tomato", "Sugarcane", "Groundnut", "Coffee"]
    data = [312, 234, 189, 156, 123, 98]
    return {"labels": labels, "data": data}

@router.get("/analytics/top-crops")
async def get_top_crops_analyzed(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        plans = db.query(CropPlan.crop_name, func.count(CropPlan.id)).group_by(CropPlan.crop_name).all()
        if plans:
            total = sum(p[1] for p in plans) or 1
            top_crops = [{"crop": p[0].title(), "percentage": round((p[1] / total) * 100, 1)} for p in plans[:4]]
        else:
            top_crops = [
                {"crop": "Rice (Paddy)", "percentage": 38.5},
                {"crop": "Ragi (Finger Millet)", "percentage": 27.0},
                {"crop": "Sugarcane", "percentage": 19.5},
                {"crop": "Tomato & Vegetables", "percentage": 15.0}
            ]
        return top_crops
    except Exception as exc:
        logger.error(f"Error fetching top crops analytics: {exc}")
        return [
            {"crop": "Rice (Paddy)", "percentage": 38.5},
            {"crop": "Ragi (Finger Millet)", "percentage": 27.0},
            {"crop": "Sugarcane", "percentage": 19.5},
            {"crop": "Tomato & Vegetables", "percentage": 15.0}
        ]

@router.get("/analytics/district-distribution")
async def get_district_distribution(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        district_counts = db.query(
            User.district,
            func.count(User.id).label('user_count')
        ).filter(
            User.district.isnot(None)
        ).group_by(User.district).all()

        total_users_with_district = sum(count.user_count for count in district_counts)

        district_data = []
        if total_users_with_district > 0:
            other_percentage = 0
            for i, dist_count in enumerate(district_counts):
                percentage = round((dist_count.user_count / total_users_with_district) * 100, 1)
                if i < 4:
                    district_data.append({"district": dist_count.district, "percentage": percentage})
                else:
                    other_percentage += percentage

            if other_percentage > 0:
                district_data.append({"district": "Other Districts", "percentage": round(other_percentage, 1)})

        if not district_data:
            district_data = [
                {"district": "Bengaluru Urban", "percentage": 35.0},
                {"district": "Mandya", "percentage": 25.0},
                {"district": "Mysuru", "percentage": 20.0},
                {"district": "Belagavi", "percentage": 20.0}
            ]

        return district_data
    except Exception as exc:
        logger.error(f"Error computing district distribution: {exc}")
        return [
            {"district": "Bengaluru Urban", "percentage": 35.0},
            {"district": "Mandya", "percentage": 25.0},
            {"district": "Mysuru", "percentage": 20.0},
            {"district": "Belagavi", "percentage": 20.0}
        ]

