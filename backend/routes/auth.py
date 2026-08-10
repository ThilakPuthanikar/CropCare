# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from sqlalchemy import text, or_
from datetime import timedelta

from ..database.database import get_db
from ..models.user import User
from ..schemas.user import Token
from ..utils.rate_limit import enforce_rate_limit
from ..utils.auth import (
    get_password_hash, 
    create_access_token,
    authenticate_user,
    authenticate_admin
)
from ..utils.validation import (
    is_strong_password,
    is_valid_district,
    is_valid_email,
    is_valid_indian_phone,
    is_valid_irrigation_type,
    is_valid_land_size,
    is_valid_name,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    enforce_rate_limit(request, "user_login", max_requests=5, window_seconds=300)
    email = None
    password = None

    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
    else:
        form_data = await request.form()
        email = (form_data.get("email") or "").strip().lower()
        password = form_data.get("password") or ""
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password required"
        )

    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    user = authenticate_user(db, email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Waiting for admin approval"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "cookie",
        "role": user.role
    })
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=(request.url.scheme == "https"),
        samesite="strict",
        max_age=1800,
        path="/",
    )
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    name = (form_data.get("name") or "").strip()
    email = (form_data.get("email") or "").strip().lower()
    phone_number = (form_data.get("phone_number") or "").strip()
    password = form_data.get("password") or ""
    district = form_data.get("district") or "Bengaluru Urban"
    land_size_str = form_data.get("land_size") or "1.0"
    irrigation_type = form_data.get("irrigation_type") or "Unknown"
    
    enforce_rate_limit(request, "register", max_requests=5, window_seconds=600)

    # Validation
    if not all([name, email, phone_number, password]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name, email, phone number, and password are required"
        )
    
    if not is_valid_name(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be 2-80 characters and contain letters and spaces only.",
        )

    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    if not is_valid_indian_phone(phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be 10 digits and start with 6, 7, 8, or 9.",
        )
    
    if not is_strong_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include uppercase, lowercase, number, and special character."
        )
    
    try:
        land_size = float(land_size_str)
        if not is_valid_land_size(land_size):
            raise ValueError
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid land size. Must be a positive number."
        )

    if not is_valid_district(district):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a valid Karnataka district.",
        )

    if not is_valid_irrigation_type(irrigation_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a valid irrigation type.",
        )

    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        name=name,
        email=email,
        phone_number=phone_number,
        password_hash=hashed_password,
        state="Karnataka",
        district=district,
        land_size=land_size,
        irrigation_type=irrigation_type,
        role="user",
        is_approved=False  # Requires admin approval
    )

    # Quick connection check to surface DB issues clearly
    try:
        db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error. Please ensure MySQL is running and accessible."
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing registration."
        )

    # Check if user already exists
    try:
        existing_user = db.query(User.id).filter(
            or_(User.email == email, User.phone_number == phone_number)
        ).first()
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database schema mismatch in users table. Re-import database.sql."
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while checking existing users."
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number already registered"
        )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except HTTPException:
        # Preserve explicit client-facing errors
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration data violates database constraints."
        )
    except OperationalError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database schema error. Import database.sql into cropcare_db and try again."
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user right now. Please try again."
        )
    except Exception as e:
        db.rollback()
        print(f"Unexpected registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )
    
    return {"message": "User registered successfully. Awaiting admin approval."}

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin/login")
async def admin_login(
    request: Request,
    db: Session = Depends(get_db)
):
    enforce_rate_limit(request, "admin_login", max_requests=5, window_seconds=300)
    form_data = await request.form()
    email = (form_data.get("email") or "").strip().lower()
    password = form_data.get("password") or ""

    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    admin_user = authenticate_admin(db, email, password)
    if not admin_user:
        admin_user = authenticate_user(db, email, password)
        if not (admin_user and getattr(admin_user, "role", "") == "admin"):
            admin_user = None

    if admin_user and getattr(admin_user, "role", "") == "admin" and getattr(admin_user, "is_approved", True):
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": admin_user.email, "role": "admin"},
            expires_delta=access_token_expires
        )
        response = JSONResponse(content={
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "cookie",
            "role": "admin"
        })
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=(request.url.scheme == "https"),
            samesite="strict",
            max_age=1800,
            path="/",
        )
        return response
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin credentials"
    )

@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token", path="/")
    return response
