import json
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models.user import User
from ..models.land_lease import LandLeaseEstimate
from ..models.ai_history import AIUsageHistory
from ..schemas.land_lease import LandLeaseInputSchema, LandLeaseResultSchema
from ..services.land_lease_valuation import calculate_land_valuation
from ..services.land_lease_ai import generate_land_lease_ai_assessment
from ..services.land_lease_report import generate_land_lease_pdf
from ..utils.auth import get_current_user
from ..config.settings import settings

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/land-leasing", tags=["Land Leasing"])
templates = Jinja2Templates(directory=PROJECT_ROOT / "frontend" / "templates")



@router.get("", response_class=HTMLResponse)
async def land_leasing_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Renders the Land Lease Estimation user interface.
    """
    user = None
    try:
        user = await get_current_user(request=request, token=None, db=db)
    except HTTPException:
        user = None

    if not user:
        # Redirect unauthenticated users to login
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse(
        "user/land_leasing.html",
        {
            "request": request,
            "user": user,
            "page_title": "Land Lease Estimation — CropCare",
        }
    )


@router.post("/estimate")
async def estimate_land_lease(
    payload: LandLeaseInputSchema,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculates land lease estimation range, runs Groq AI strategic assessment,
    saves record in database, and returns formatted result payload.
    """
    try:
        # 1. Calculate Valuation Range & Multipliers
        valuation = calculate_land_valuation(payload)

        # 2. Obtain Groq API Key
        groq_api_key = getattr(settings, "GROQ_API_KEY", None)
        if not groq_api_key:
            keys = getattr(settings, "GROQ_API_KEYS", [])
            if keys:
                groq_api_key = keys[0]

        # 3. Generate AI Strategic Assessment
        ai_assessment = generate_land_lease_ai_assessment(
            input_data=payload,
            valuation=valuation,
            api_key=groq_api_key
        )

        # 4. Generate Unique Report ID
        short_code = uuid.uuid4().hex[:6].upper()
        report_id = f"LL-{datetime.now().strftime('%Y%m')}-{short_code}"

        # 5. Persist Record to LandLeaseEstimate DB Table
        factors_data = {
            "positive_factors": valuation["positive_factors"],
            "negative_factors": valuation["negative_factors"],
        }

        estimate_record = LandLeaseEstimate(
            user_id=current_user.id,
            report_id=report_id,
            state=payload.state,
            district=payload.district,
            taluk=payload.taluk,
            village=payload.village,
            input_size=payload.input_size,
            input_unit=payload.input_unit,
            acres=valuation["acres"],
            land_type=payload.land_type,
            soil_type=payload.soil_type,
            current_use=payload.current_use,
            intended_use=payload.intended_use,
            land_condition=payload.land_condition,
            water_availability=payload.water_availability,
            water_source=payload.water_source,
            irrigation_type=payload.irrigation_type,
            electricity_available=payload.electricity_available,
            electricity_reliability=payload.electricity_reliability,
            connection_type=payload.connection_type,
            road_access=payload.road_access,
            transport_access=payload.transport_access,
            distance_main_road_km=payload.distance_main_road_km,
            distance_market_km=payload.distance_market_km,
            infrastructure_json=json.dumps(payload.infrastructure or []),
            lease_duration_years=payload.lease_duration_years,
            additional_notes=payload.additional_notes,
            base_rate_per_acre=valuation["base_rate_per_acre"],
            calculated_min_price=valuation["calculated_min_price"],
            calculated_max_price=valuation["calculated_max_price"],
            confidence_score=valuation["confidence_score"],
            confidence_reasons_json=json.dumps(valuation["confidence_reasons"]),
            factors_json=json.dumps(factors_data),
            ai_analysis_json=json.dumps(ai_assessment),
        )

        db.add(estimate_record)

        # 6. Also Log into AIUsageHistory Table for AI Feature Auditability
        ai_history_entry = AIUsageHistory(
            user_id=current_user.id,
            feature_type="land_lease_estimation",
            input_payload=json.dumps({
                "report_id": report_id,
                "district": payload.district,
                "input_size": payload.input_size,
                "input_unit": payload.input_unit,
                "acres": valuation["acres"],
            }),
            output_payload=json.dumps({
                "min_price": valuation["calculated_min_price"],
                "max_price": valuation["calculated_max_price"],
                "confidence": valuation["confidence_score"],
            }),
        )
        db.add(ai_history_entry)

        db.commit()
        db.refresh(estimate_record)

        return {
            "status": "success",
            "report_id": report_id,
            "acres": valuation["acres"],
            "input_size": payload.input_size,
            "input_unit": payload.input_unit,
            "district": payload.district,
            "state": payload.state,
            "base_rate_per_acre": valuation["base_rate_per_acre"],
            "calculated_min_price": valuation["calculated_min_price"],
            "calculated_max_price": valuation["calculated_max_price"],
            "monthly_min_price": valuation["monthly_min_price"],
            "monthly_max_price": valuation["monthly_max_price"],
            "per_acre_min": valuation["per_acre_min"],
            "per_acre_max": valuation["per_acre_max"],
            "confidence_score": valuation["confidence_score"],
            "confidence_reasons": valuation["confidence_reasons"],
            "positive_factors": valuation["positive_factors"],
            "negative_factors": valuation["negative_factors"],
            "ai_analysis": ai_assessment,
            "created_at": estimate_record.created_at.strftime("%d %b %Y, %I:%M %p"),
        }

    except Exception as exc:
        db.rollback()
        logger.error(f"Error in estimate_land_lease: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate land lease estimate: {str(exc)}"
        )


@router.get("/history")
async def get_land_lease_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user's estimation history list.
    """
    estimates = (
        db.query(LandLeaseEstimate)
        .filter(LandLeaseEstimate.user_id == current_user.id)
        .order_by(LandLeaseEstimate.created_at.desc())
        .all()
    )

    history_items = []
    for item in estimates:
        history_items.append({
            "id": item.id,
            "report_id": item.report_id,
            "district": item.district,
            "state": item.state,
            "input_size": item.input_size,
            "input_unit": item.input_unit,
            "acres": item.acres,
            "calculated_min_price": item.calculated_min_price,
            "calculated_max_price": item.calculated_max_price,
            "confidence_score": item.confidence_score,
            "water_availability": item.water_availability,
            "created_at": item.created_at.strftime("%d %b %Y, %I:%M %p"),
        })

    return {"status": "success", "history": history_items}


@router.get("/history/{report_id}")
async def get_land_lease_detail(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full details for a single land lease estimation by report_id.
    """
    estimate = (
        db.query(LandLeaseEstimate)
        .filter(
            LandLeaseEstimate.report_id == report_id,
            LandLeaseEstimate.user_id == current_user.id
        )
        .first()
    )

    if not estimate:
        raise HTTPException(status_code=404, detail="Land lease estimate report not found.")

    infra = []
    if estimate.infrastructure_json:
        try:
            infra = json.loads(estimate.infrastructure_json)
        except Exception:
            pass

    reasons = []
    if estimate.confidence_reasons_json:
        try:
            reasons = json.loads(estimate.confidence_reasons_json)
        except Exception:
            pass

    factors = {"positive_factors": [], "negative_factors": []}
    if estimate.factors_json:
        try:
            factors = json.loads(estimate.factors_json)
        except Exception:
            pass

    ai_analysis = {}
    if estimate.ai_analysis_json:
        try:
            ai_analysis = json.loads(estimate.ai_analysis_json)
        except Exception:
            pass

    min_price = estimate.calculated_min_price
    max_price = estimate.calculated_max_price
    acres = max(0.01, estimate.acres)

    return {
        "status": "success",
        "report_id": estimate.report_id,
        "district": estimate.district,
        "state": estimate.state,
        "taluk": estimate.taluk,
        "village": estimate.village,
        "input_size": estimate.input_size,
        "input_unit": estimate.input_unit,
        "acres": estimate.acres,
        "land_type": estimate.land_type,
        "soil_type": estimate.soil_type,
        "current_use": estimate.current_use,
        "intended_use": estimate.intended_use,
        "water_availability": estimate.water_availability,
        "water_source": estimate.water_source,
        "irrigation_type": estimate.irrigation_type,
        "electricity_available": estimate.electricity_available,
        "electricity_reliability": estimate.electricity_reliability,
        "road_access": estimate.road_access,
        "transport_access": estimate.transport_access,
        "infrastructure": infra,
        "lease_duration_years": estimate.lease_duration_years,
        "base_rate_per_acre": estimate.base_rate_per_acre,
        "calculated_min_price": min_price,
        "calculated_max_price": max_price,
        "monthly_min_price": round(min_price / 12.0, -1),
        "monthly_max_price": round(max_price / 12.0, -1),
        "per_acre_min": round(min_price / acres, -1),
        "per_acre_max": round(max_price / acres, -1),
        "confidence_score": estimate.confidence_score,
        "confidence_reasons": reasons,
        "positive_factors": factors.get("positive_factors", []),
        "negative_factors": factors.get("negative_factors", []),
        "ai_analysis": ai_analysis,
        "created_at": estimate.created_at.strftime("%d %b %Y, %I:%M %p"),
    }


@router.get("/report/{report_id}")
async def download_land_lease_report_pdf(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates and returns the downloadable PDF report for the given estimate report_id.
    """
    estimate = (
        db.query(LandLeaseEstimate)
        .filter(
            LandLeaseEstimate.report_id == report_id,
            LandLeaseEstimate.user_id == current_user.id
        )
        .first()
    )

    if not estimate:
        raise HTTPException(status_code=404, detail="Land lease estimate report not found.")

    pdf_bytes = generate_land_lease_pdf(
        estimate=estimate,
        user_name=getattr(current_user, "name", "Farmer / Landowner")
    )


    filename = f"Land_Lease_Report_{estimate.report_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
