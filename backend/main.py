import os
import sys
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from .config.settings import settings
from .database.database import engine, Base, SessionLocal
from .models.scheme import Scheme
from .models.price import Price
from .models.user import User
from .models.admin import Admin
from .routes import auth, user, admin, land_leasing
from .utils.schemes import DEFAULT_SCHEMES, serialize_text_list
from .utils.auth import get_password_hash

# Create tables if they don't already exist (including prices and admins)
Base.metadata.create_all(bind=engine)


def _get_cors_origins():
    origins = [origin.strip() for origin in (settings.CORS_ORIGINS or "").split(",")]
    return [origin for origin in origins if origin]


def ensure_schema_columns():
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "profile_photo" not in user_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN profile_photo VARCHAR(500) NULL")
                )
        if "phone_number" not in user_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(10) NULL")
                )
                try:
                    connection.execute(
                        text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users (phone_number)")
                    )
                except Exception:
                    pass

    if "schemes" in inspector.get_table_names():
        scheme_columns = {column["name"] for column in inspector.get_columns("schemes")}
        scheme_column_defs = {
            "type": "ALTER TABLE schemes ADD COLUMN type VARCHAR(50) NOT NULL DEFAULT 'national'",
            "beneficiary": "ALTER TABLE schemes ADD COLUMN beneficiary VARCHAR(100) NULL",
            "eligibility": "ALTER TABLE schemes ADD COLUMN eligibility TEXT NULL",
            "duration": "ALTER TABLE schemes ADD COLUMN duration VARCHAR(255) NULL",
            "icon": "ALTER TABLE schemes ADD COLUMN icon VARCHAR(100) NULL",
            "state": "ALTER TABLE schemes ADD COLUMN state VARCHAR(100) NULL",
            "district": "ALTER TABLE schemes ADD COLUMN district VARCHAR(100) NULL",
            "is_active": "ALTER TABLE schemes ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE",
        }
        missing_scheme_columns = [
            ddl for column_name, ddl in scheme_column_defs.items()
            if column_name not in scheme_columns
        ]
        if missing_scheme_columns:
            with engine.begin() as connection:
                for ddl in missing_scheme_columns:
                    connection.execute(text(ddl))

    if "mandi_prices" in inspector.get_table_names():
        mandi_columns = {column["name"] for column in inspector.get_columns("mandi_prices")}
        mandi_column_defs = {
            "crop_name": "ALTER TABLE mandi_prices ADD COLUMN crop_name VARCHAR(120) NOT NULL DEFAULT ''",
            "variety": "ALTER TABLE mandi_prices ADD COLUMN variety VARCHAR(120) NULL",
            "grade": "ALTER TABLE mandi_prices ADD COLUMN grade VARCHAR(120) NULL",
            "district": "ALTER TABLE mandi_prices ADD COLUMN district VARCHAR(120) NOT NULL DEFAULT ''",
            "mandi_name": "ALTER TABLE mandi_prices ADD COLUMN mandi_name VARCHAR(180) NOT NULL DEFAULT ''",
            "arrival": "ALTER TABLE mandi_prices ADD COLUMN arrival FLOAT NULL",
            "unit": "ALTER TABLE mandi_prices ADD COLUMN unit VARCHAR(50) NULL",
            "price_per_quintal": "ALTER TABLE mandi_prices ADD COLUMN price_per_quintal FLOAT NOT NULL DEFAULT 0",
            "min_price": "ALTER TABLE mandi_prices ADD COLUMN min_price FLOAT NULL",
            "max_price": "ALTER TABLE mandi_prices ADD COLUMN max_price FLOAT NULL",
            "price_date": "ALTER TABLE mandi_prices ADD COLUMN price_date DATE NULL",
            "last_updated": "ALTER TABLE mandi_prices ADD COLUMN last_updated TIMESTAMP WITH TIME ZONE NULL",
        }
        missing_mandi_columns = [
            ddl for column_name, ddl in mandi_column_defs.items()
            if column_name not in mandi_columns
        ]
        if missing_mandi_columns:
            with engine.begin() as connection:
                for ddl in missing_mandi_columns:
                    connection.execute(text(ddl))
        with engine.begin() as connection:
            try:
                connection.execute(text("DROP INDEX IF EXISTS uq_mandi_crop_market"))
            except Exception:
                pass
            try:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS uq_mandi_crop_market_week "
                        "ON mandi_prices (crop_name, district, mandi_name, price_date)"
                    )
                )
            except Exception:
                pass



def seed_default_schemes():
    db = SessionLocal()
    try:
        new_records = []
        for scheme_data in DEFAULT_SCHEMES:
            existing_scheme = db.query(Scheme).filter(Scheme.title == scheme_data["title"]).first()
            if existing_scheme:
                existing_scheme.description = scheme_data["description"]
                existing_scheme.type = scheme_data["type"]
                existing_scheme.beneficiary = scheme_data["beneficiary"]
                existing_scheme.benefits = scheme_data["benefits"]
                existing_scheme.eligibility = scheme_data["eligibility"]
                existing_scheme.documents_required = serialize_text_list(scheme_data["documents_required"])
                existing_scheme.steps_to_apply = serialize_text_list(scheme_data["steps_to_apply"])
                existing_scheme.duration = scheme_data["duration"]
                existing_scheme.official_link = scheme_data["official_link"]
                existing_scheme.icon = scheme_data["icon"]
                existing_scheme.state = scheme_data["state"]
                existing_scheme.district = scheme_data["district"]
                existing_scheme.is_active = scheme_data["is_active"]
            else:
                new_records.append(
                    Scheme(
                        title=scheme_data["title"],
                        description=scheme_data["description"],
                        type=scheme_data["type"],
                        beneficiary=scheme_data["beneficiary"],
                        benefits=scheme_data["benefits"],
                        eligibility=scheme_data["eligibility"],
                        documents_required=serialize_text_list(scheme_data["documents_required"]),
                        steps_to_apply=serialize_text_list(scheme_data["steps_to_apply"]),
                        duration=scheme_data["duration"],
                        official_link=scheme_data["official_link"],
                        icon=scheme_data["icon"],
                        state=scheme_data["state"],
                        district=scheme_data["district"],
                        is_active=scheme_data["is_active"],
                    )
                )
        if new_records:
            db.add_all(new_records)
        db.commit()
    finally:
        db.close()


def ensure_admin_user():
    db = SessionLocal()
    try:
        admin_email = (settings.ADMIN_EMAIL or "").strip().lower()
        admin_password = settings.ADMIN_PASSWORD or ""
        if not admin_email or not admin_password:
            return

        hashed_password = get_password_hash(admin_password)

        # 1. Migrate any existing admin records out of `users` table into `admins` table first
        old_user_admins = db.query(User).filter(User.role == "admin").all()
        for old_u in old_user_admins:
            existing_admin = db.query(Admin).filter(Admin.email == old_u.email).first()
            if not existing_admin:
                new_a = Admin(
                    name=old_u.name or "System Admin",
                    email=old_u.email,
                    password_hash=old_u.password_hash,
                    role="admin",
                    is_approved=True,
                    profile_photo=old_u.profile_photo,
                )
                db.add(new_a)
            db.delete(old_u)
        db.commit()

        # 2. Ensure primary admin account exists inside `admins` table
        admin_user = db.query(Admin).filter(Admin.email == admin_email).first()
        if admin_user:
            admin_user.role = "admin"
            admin_user.is_approved = True
            admin_user.password_hash = hashed_password
        else:
            admin_user = Admin(
                name="Admin User",
                email=admin_email,
                password_hash=hashed_password,
                role="admin",
                is_approved=True,
            )
            db.add(admin_user)
        db.commit()
    finally:
        db.close()


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_schema_columns()
    seed_default_schemes()
    ensure_admin_user()
    print("Starting CropCare application...")
    yield

app = FastAPI(title="CropCare API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def enforce_csrf_header(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        path = request.url.path
        if path.startswith("/user/") or path.startswith("/admin/") or path == "/auth/logout":
            if request.headers.get("X-Requested-With") != "XMLHttpRequest":
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Missing anti-CSRF custom header."}
                )
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/user/proxy-krama"):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
    else:
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https: blob:; script-src 'self' 'unsafe-inline' https: cdn.tailwindcss.com cdnjs.cloudflare.com cdn.jsdelivr.net www.chatbase.co; style-src 'self' 'unsafe-inline' https: fonts.googleapis.com cdnjs.cloudflare.com; font-src 'self' https: data: fonts.gstatic.com cdnjs.cloudflare.com; frame-src 'self' https: https://krama.karnataka.gov.in; connect-src 'self' https: www.chatbase.co;"
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/features", response_class=HTMLResponse)
async def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(land_leasing.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
