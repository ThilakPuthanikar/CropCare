# CropCare — Project Architecture & File Directory Guide

This document provides the complete directory structure of the **CropCare** precision agriculture web platform, followed by a detailed 5–6 line functional description for every directory and file in the codebase.

---

## 📁 Exact Directory Tree

```
CropCare/
├── .env
├── .env.example
├── .gitignore
├── Procfile
├── PROJECT_STRUCTURE.md
├── nixpacks.toml
├── requirements.txt
├── start.bat
├── stop.bat
├── vercel.json
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ad.py
│   │   ├── admin.py
│   │   ├── ai_history.py
│   │   ├── crop_plan.py
│   │   ├── district_rainfall.py
│   │   ├── land_lease.py
│   │   ├── price.py
│   │   ├── scheme.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── land_leasing.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ad.py
│   │   ├── admin.py
│   │   ├── land_lease.py
│   │   ├── price.py
│   │   ├── scheme.py
│   │   └── user.py
│   ├── services/
│   │   ├── land_lease_ai.py
│   │   ├── land_lease_report.py
│   │   ├── land_lease_valuation.py
│   │   └── mandi_service.py
│   └── utils/
│       ├── __init__.py
│       ├── ai.py
│       ├── auth.py
│       ├── crop_planner.py
│       ├── mandi_prices.py
│       ├── rate_limit.py
│       ├── schemes.py
│       ├── validation.py
│       └── weather.py
├── database/
│   ├── mysql/
│   │   └── database.sql
│   ├── postgresql/
│   │   └── database_postgresql.sql
│   └── migrations/
│       └── migrate_mysql_to_neon.py
├── docs/
│   ├── DEPLOYMENT.md
│   ├── DESIGN.md
│   ├── PRODUCT.md
│   ├── PROJECT_SPECIFICATION.md
│   ├── README.md
│   └── how_to_run.txt
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │       ├── BLACK_COTTON_SOIL.png
│   │       ├── COASTAL_ALLUVIAL_SOIL.png
│   │       ├── FOREST_SOIL.png
│   │       ├── LATERITE_SOIL.png
│   │       ├── RED_SOIL.png
│   │       ├── REED_SANDY_LOAM_SOIL.png
│   │       ├── logo.png
│   │       └── logo_clean.png
│   ├── templates/
│   │   ├── about.html
│   │   ├── admin_login.html
│   │   ├── base.html
│   │   ├── contact.html
│   │   ├── features.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── admin/
│   │   │   ├── analytics.html
│   │   │   ├── dashboard.html
│   │   │   ├── manage_admins.html
│   │   │   ├── manage_ads.html
│   │   │   ├── manage_prices.html
│   │   │   ├── manage_schemes.html
│   │   │   └── manage_users.html
│   │   ├── partials/
│   │   │   ├── common_modals.html
│   │   │   └── footer.html
│   │   └── user/
│   │       ├── crop_planner.html
│   │       ├── crop_recommendation.html
│   │       ├── dashboard.html
│   │       ├── disease_diagnosis.html
│   │       ├── gov_schemes.html
│   │       ├── input_suggestions.html
│   │       ├── land_leasing.html
│   │       ├── mandi_tracking.html
│   │       ├── profile.html
│   │       ├── soil_library.html
│   │       └── weather.html
│   └── uploads/
│       └── profiles/
├── scripts/
│   ├── launcher.ps1
│   ├── start.bat
│   ├── stop.bat
│   └── stopper.ps1
└── tests/
    └── test_land_leasing.py
```

---

## 📑 Comprehensive Folder & File Explanations

### 🌐 Root Directory Files

#### `.env`
Environment file containing sensitive local runtime configuration settings and credentials.
It defines critical environment variables including `DATABASE_URL` (Neon PostgreSQL cloud connection string), `GROQ_API_KEY`, `JWT_SECRET`, `CLOUDINARY_URL`, and server port bindings.
Because it stores private API tokens and database passwords, it is ignored by Git to prevent security leaks.
It is automatically read by Pydantic's `BaseSettings` during FastAPI application startup.
Developers configure their local environment by editing variables in this file.

#### `.env.example`
Template version of the environment configuration file distributed to the repository.
It lists all required environment variable keys alongside placeholder values and documentation notes without disclosing actual passwords or secrets.
New developers copy this file to `.env` when setting up CropCare for local development or deployment.
It guarantees that all necessary configuration variables (database credentials, API keys, JWT secrets) are clearly defined.
It serves as the authoritative specification for required environment variables across local, staging, and production environments.

#### `.gitignore`
Git version control exclusion file specifying files and directories to omit from commit history.
It ignores Python bytecode (`__pycache__`, `*.pyc`), virtual environments (`venv/`), temporary runtime logs, uploaded images, and sensitive local secrets (`.env`).
It prevents accidental commits of build artifacts, scratch scripts, local database backups, and environment-specific caches.
It ensures the repository remains lean, secure, and clean across team environments.
It explicitly tracks core source code while filtering transient IDE and OS metadata.

#### `Procfile`
Process configuration file used by PaaS deployment hosts like Railway, Heroku, and Dokku.
It defines the primary web process command: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
It instructs container runners how to initialize the FastAPI server process on platform boot.
It ensures proper binding to environment-provided PORT variables during cloud deployments.
It allows cloud hosting providers to automatically manage worker processes and health monitoring.

#### `PROJECT_STRUCTURE.md`
Master architecture and directory documentation guide for the CropCare platform.
It documents the visual folder hierarchy and complete 5–6 line functional breakdowns for every folder and file in the codebase.
It provides developers, maintainers, and automated tools with authoritative guidance on component responsibilities.
It ensures long-term repository maintainability following code reorganizations.
It acts as the reference blueprint for project navigation.

#### `nixpacks.toml`
Build configuration file for Nixpacks container builders used by hosting platforms like Railway and Render.
It configures Python 3.11 environment setup, system package dependencies, and build caching rules.
It defines exact build phase installation steps: `pip install -r requirements.txt`.
It specifies start commands: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
It ensures deterministic, reproducible container builds across cloud deployment pipelines.

#### `requirements.txt`
Python package dependency manifest listing all third-party libraries required by CropCare.
It specifies pinned versions for `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg[binary]`, `pydantic`, `groq`, `reportlab`, `requests`, and `jinja2`.
It ensures complete dependency parity across local development machines and cloud deployment servers.
It enables automated environment installation via `pip install -r requirements.txt`.
It contains essential tools for database ORM, AI completion APIs, PDF report generation, and security hashing.

#### `start.bat`
Root Windows batch script entry point delegating execution to `scripts/start.bat`.
It resolves project directory paths dynamically from `%~dp0`.
It invokes `scripts/launcher.ps1` with bypassed execution policies for developer convenience.
It provides one-click launching for backend servers, browser opening, and Ngrok tunnels.
It ensures seamless local execution without requiring terminal navigation into `scripts/`.

#### `stop.bat`
Root Windows batch script entry point delegating execution to `scripts/stop.bat`.
It resolves project directory paths dynamically from `%~dp0`.
It invokes `scripts/stopper.ps1` in PowerShell to safely terminate background Uvicorn and Ngrok processes.
It ensures clean local shutdown without leaving process locks on port 8000.
It provides a simple one-click command for stopping all CropCare background tasks.

#### `vercel.json`
Deployment configuration file for hosting CropCare static assets and frontend routing on Vercel CDN.
It configures build routes, header overrides, static file redirections, and CORS permissions.
It handles client-side route rewrites and security header enforcement (`X-Frame-Options`, `Content-Security-Policy`).
It allows fast static asset distribution across Vercel's global edge network.
It provides fallback routing rules for static HTML templates and public assets.

---

### ⚙️ `backend/` — Core Backend Application

#### `backend/__init__.py`
Package initialization file marking `backend` as a Python package directory.
It exposes core package modules and allows clean relative imports across application sub-packages.
It enables structured module resolution for models, routes, schemas, services, and utilities.
It maintains Python package hierarchy standards across the application codebase.
It facilitates automated test suite discovery and modular architecture organization.

#### `backend/main.py`
Main FastAPI application entry point and central server setup module.
It instantiates the `FastAPI` app with lifespan event handlers (`ensure_schema_columns`, `seed_default_schemes`, `ensure_admin_user`).
It derives `PROJECT_ROOT` dynamically using `Path(__file__).resolve().parent.parent`.
It mounts `frontend/static` under `/static` and `frontend/uploads` under `/static/uploads`, and configures Jinja2 templates from `frontend/templates`.
It registers all API routers (`auth`, `user`, `admin`, `land_leasing`) and renders public web pages (`/`, `/about`, `/contact`, `/features`).

---

### 🛠️ `backend/config/` — Application Configuration

#### `backend/config/__init__.py`
Package initialization file for the backend configuration package.
It exports configuration symbols like `settings` for clean import statements throughout the backend.
It organizes settings management and ensures configuration singletons across worker threads.
It enforces structured package boundaries for environment variable parsers.
It supports modular configuration importing across database, route, and service layers.

#### `backend/config/settings.py`
Pydantic settings configuration module for loading and validating environment variables.
It defines `Settings` class inheriting from `BaseSettings` reading from `.env` files.
It validates database connection strings (`DATABASE_URL`), JWT secret keys, API keys (`GROQ_API_KEY`), and server configuration.
It automatically normalizes PostgreSQL URIs (converting `postgres://` to `postgresql+psycopg://` for SQLAlchemy 2.0).
It provides typed configuration properties accessible anywhere in the application via `from .config.settings import settings`.

---

### 🗄️ `backend/database/` — Database Management

#### `backend/database/__init__.py`
Package initialization file for the database management sub-package.
It exposes database connection engines, session factories, and Base metadata classes.
It simplifies database dependency imports across models, routes, and services.
It maintains clean sub-package boundaries for data access layer modules.
It supports unified session lifecycle management across FastAPI requests.

#### `backend/database/database.py`
SQLAlchemy database engine configuration and session lifecycle management module.
It initializes `create_engine` connected to Neon PostgreSQL with connection pooling (`pool_pre_ping=True`, `pool_size=10`).
It instantiates `SessionLocal` (`sessionmaker`) for managing thread-local database transactions.
It defines `Base = declarative_base()` as the parent class for all SQLAlchemy ORM models.
It provides the `get_db()` dependency generator yielding database sessions to FastAPI route handlers with automatic cleanup.

---

### 📊 `backend/models/` — SQLAlchemy ORM Data Models

#### `backend/models/__init__.py`
Package initialization file exporting all SQLAlchemy ORM data models.
It imports `User`, `Admin`, `Ad`, `Scheme`, `CropPlan`, `Price`, `DistrictRainfall`, `AIUsageHistory`, and `LandLeaseEstimate`.
It ensures all database tables are registered under `Base.metadata` for automated creation via `Base.metadata.create_all()`.
It provides a single import location for database models throughout the backend.
It facilitates clean schema introspection and database migration operations.

#### `backend/models/ad.py`
SQLAlchemy ORM model defining the `ads` table for agricultural promotional advertisements.
It stores ad attributes: `id`, `title`, `description`, `image_url`, `target_url`, `is_active`, and timestamp tracking fields.
It enables administrators to create, feature, and manage agricultural product ads displayed on user dashboards.
It provides active status filtering for dynamic ad rotation in farmer interfaces.
It supports promotional content management across public and user dashboard layouts.

#### `backend/models/admin.py`
SQLAlchemy ORM model defining the `admins` table for platform administrative users.
It stores admin credentials: `id`, `name`, `email`, `password_hash`, `role` ("admin"), `is_approved`, and `profile_photo`.
It decouples system administrator authentication from standard farmer accounts for security isolation.
It supports administrative authorization checks across management endpoints.
It records account creation and modification timestamps for administrative audit trails.

#### `backend/models/ai_history.py`
SQLAlchemy ORM model defining the `ai_usage_history` table for tracking AI features.
It stores record attributes: `id`, `user_id`, `feature_type` (e.g. crop suggestion, disease diagnosis, land lease valuation), `input_payload`, `output_payload`, and timestamp.
It logs all user interactions with Groq AI services for auditability, analytics, and history retrieval.
It maintains user-specific historical records accessible from farmer dashboard tabs.
It enables administrators to monitor AI usage volume and model performance metrics.

#### `backend/models/crop_plan.py`
SQLAlchemy ORM model defining the `crop_plans` table for farmer seasonal planning.
It stores plan details: `id`, `user_id`, `crop_name`, `field_size_acres`, `sowing_date`, `expected_harvest_date`, `status`, and `stages_json`.
It serializes step-by-step growth stages, irrigation milestones, and fertilizer schedules in JSON format.
It supports interactive crop plan tracking, stage completion toggling, and live reminder alerts.
It links farmer accounts to personalized agricultural action plans.

#### `backend/models/district_rainfall.py`
SQLAlchemy ORM model defining the `district_rainfall` table for Karnataka climate baselines.
It stores regional attributes: `id`, `district_name`, `annual_rainfall_mm`, `monsoon_start_month`, `primary_soil_type`, and climate notes.
It provides historical rainfall data for Karnataka's 31 districts to power crop suitability algorithms.
It acts as a reference dataset for water availability and irrigation recommendations.
It enables location-aware precision farming calculations across farmer user routes.

#### `backend/models/land_lease.py`
SQLAlchemy ORM model defining the `land_lease_estimates` table for land valuation records.
It stores comprehensive land attributes: `id`, `user_id`, `report_id`, location (`state`, `district`, `taluk`), land size, water availability, electricity, and road access.
It records calculated valuation bounds (`calculated_min_price`, `calculated_max_price`), confidence scores, positive/negative price drivers, and Groq AI assessment JSON.
It supports land lease estimation history viewing and downloadable PDF report generation.
It links land valuation records to authenticated farmer user accounts.

#### `backend/models/price.py`
SQLAlchemy ORM model defining the `mandi_prices` table for market price tracking.
It stores commodity pricing fields: `id`, `crop_name`, `variety`, `grade`, `district`, `mandi_name`, `price_per_quintal`, `min_price`, `max_price`, `price_date`, and `last_updated`.
It caches live market prices fetched from official Karnataka Mandi portals (`krama.karnataka.gov.in`).
It supports historic price trend analysis, commodity search filtering, and price alerts.
It ensures fast database queries for mandi price tracking dashboard widgets.

#### `backend/models/scheme.py`
SQLAlchemy ORM model defining the `schemes` table for government agricultural welfare programs.
It stores program attributes: `id`, `title`, `description`, `type` ("national" / "state"), `beneficiary`, `benefits`, `eligibility`, `duration`, `official_link`, and location filters.
It stores required application documents and step-by-step application guides in JSON format.
It enables farmers to filter, search, and discover government subsidies tailored to their location.
It allows administrators to seed, add, update, and manage official welfare schemes.

#### `backend/models/user.py`
SQLAlchemy ORM model defining the primary `users` table for farmer accounts.
It stores user profile data: `id`, `name`, `email`, `password_hash`, `role` ("user"), `is_approved`, `state`, `district`, `phone_number`, `land_size`, `irrigation_type`, and `profile_photo`.
It serves as the core user entity across authentication, crop recommendations, weather alerts, and land lease estimations.
It manages relationships with user-owned entities like crop plans, AI usage histories, and land lease estimates.
It tracks profile registration dates and last update timestamps for account management.

---

### 🛣️ `backend/routes/` — FastAPI API Routers

#### `backend/routes/__init__.py`
Package initialization file exporting all FastAPI router instances.
It imports `auth`, `user`, `admin`, and `land_leasing` routers for clean inclusion in `main.py`.
It maintains modular routing architecture across authentication, user features, and administrative APIs.
It simplifies application router registration and OpenAPI documentation grouping.
It supports unified middleware enforcement across route groups.

#### `backend/routes/admin.py`
FastAPI router module implementing administrative dashboard API endpoints under `/admin`.
It provides endpoints for admin authentication, user approval management (`PUT /admin/users/{id}/approve`), user deletion, and admin account management.
It handles CRUD operations for government schemes, mandi prices, and promotional dashboard ads (`/admin/ads`).
It delivers administrative analytics metrics (`GET /admin/analytics`), system usage totals, and activity logs.
It enforces strict administrative role authorization checks (`role == 'admin'`) across all management endpoints using Jinja2 templates from `frontend/templates`.

#### `backend/routes/auth.py`
FastAPI router module handling user authentication and registration endpoints under `/auth`.
It processes farmer user registration (`POST /auth/signup`) with input validation and password hashing.
It handles user and admin login authentication (`POST /auth/login`), generating signed JWT access tokens stored in HTTP-only cookies.
It provides session logout endpoints (`POST /auth/logout`) that clear authorization cookies.
It renders authentication templates (`login.html`, `signup.html`, `admin_login.html`) from `frontend/templates`.

#### `backend/routes/land_leasing.py`
FastAPI router module implementing the Land Lease Estimation feature endpoints under `/user/land-leasing`.
It renders the responsive land leasing user interface (`GET /user/land-leasing`) from `frontend/templates/user/land_leasing.html`.
It processes form submissions (`POST /user/land-leasing/estimate`), invoking valuation algorithms, Groq AI assessments, and database persistence.
It provides user estimation history retrieval (`GET /user/land-leasing/history` & `/history/{report_id}`).
It generates and streams downloadable PDF valuation reports (`GET /user/land-leasing/report/{report_id}`) using ReportLab.

#### `backend/routes/user.py`
FastAPI router module serving farmer user dashboard endpoints and core AI features under `/user`.
It renders user dashboard HTML templates from `frontend/templates/user/`, profile management pages, and weather interfaces.
It provides AI endpoints for crop recommendations (`POST /user/crop-recommendation`), disease diagnosis (`POST /user/disease-diagnosis`), and input suggestions.
It manages profile photo uploads stored locally under `frontend/uploads/profiles/`.
It delivers mandi price tracking data (`/user/mandi-tracking`), proxying live Karnataka Mandi reports, and government scheme listings.

---

### 📐 `backend/schemas/` — Pydantic Validation Schemas

#### `backend/schemas/__init__.py`
Package initialization file exporting all Pydantic validation schemas.
It exports request/response schemas for users, admins, ads, schemes, prices, and land lease estimations.
It ensures clean schema imports across route handlers and service modules.
It enforces structured data validation boundaries across API contracts.
It supports automated OpenAPI documentation generation.

#### `backend/schemas/ad.py`
Pydantic schemas for validating advertisement data payloads.
It defines `AdCreateSchema`, `AdUpdateSchema`, and `AdResponseSchema` for ad management endpoints.
It validates title length, description text, image URLs, target web links, and active display toggles.
It ensures valid data formats before persisting promotional ads to the database.
It structures API responses for advertisement dashboard widgets.

#### `backend/schemas/admin.py`
Pydantic schemas for administrative data structures and response payloads.
It defines `AdminResponseSchema`, `UserApprovalSchema`, and `SystemAnalyticsSchema`.
It structures administrative overview metrics: total user count, pending approvals, active schemes, and AI usage volume.
It validates admin profile update payloads and password reset requests.
It guarantees strict typing across administrative management routes.

#### `backend/schemas/land_lease.py`
Pydantic schemas for validating Land Lease Estimation inputs and responses.
It defines `LandLeaseInputSchema` validating land size (>0), measurement units (`Acre`, `Hectare`, `Guntha`), district names, water availability, electricity, and road access.
It defines `LandLeaseResultSchema` structuring estimation responses, valuation bounds, confidence scores, price drivers, and AI assessments.
It includes custom Pydantic validators enforcing unit string choices and numeric ranges.
It ensures API payload integrity before executing valuation algorithms.

#### `backend/schemas/price.py`
Pydantic schemas for validating Mandi price data models and API parameters.
It defines `MandiPriceCreateSchema`, `MandiPriceFilterSchema`, and `MandiPriceResponseSchema`.
It validates commodity crop names, district names, mandi market names, arrival quantities, and price per quintal figures.
It supports price trend query filtering by crop, district, and date ranges.
It ensures data validation when scraping or updating mandi market prices.

#### `backend/schemas/scheme.py`
Pydantic schemas for validating government scheme payloads and filter options.
It defines `SchemeCreateSchema`, `SchemeUpdateSchema`, and `SchemeResponseSchema`.
It validates scheme titles, eligibility criteria, beneficiary descriptions, subsidy details, and external portal links.
It handles serialization and validation of document requirements and application step lists.
It structures scheme search responses for farmer discovery interfaces.

#### `backend/schemas/user.py`
Pydantic schemas for user profile validation, registration, and update payloads.
It defines `UserSignupSchema`, `UserLoginSchema`, `UserProfileUpdateSchema`, and `UserResponseSchema`.
It validates email syntax, phone numbers, state/district names, land area figures, and password complexity.
It prevents invalid or malicious input during user registration and profile editing.
It sanitizes user output objects, excluding password hashes from API responses.

---

### 🔌 `backend/services/` — Business Logic Services

#### `backend/services/land_lease_ai.py`
Service module integrating Groq AI (`llama-3.3-70b-versatile`) for strategic land lease assessments.
It constructs structured prompts passing land details, location attributes, and backend-calculated price ranges.
It instructs Groq AI to explain the deterministic valuation numbers without altering or inventing price figures.
It returns structured JSON containing overview summaries, range explanations, positive/negative drivers, and strategic negotiation advice.
It includes a robust fallback response generator ensuring graceful application behavior if Groq API is offline.

#### `backend/services/land_lease_report.py`
PDF generation service building executive, downloadable Land Lease Reports using ReportLab.
It embeds official CropCare branding (`frontend/static/images/logo.png`), Report ID, date, and user details in an executive layout.
It formats valuation bounds (`Rs. X,XXX - Rs. Y,YYY / year`), monthly breakdown, per-acre rates, and confidence badges.
It renders property overview tables, price drivers grids, AI strategic advice callouts, and mandatory legal disclaimers.
It includes `clean_pdf_text()` sanitizers replacing unsupported unicode symbols with clean ASCII characters to eliminate missing glyph boxes (`■`).

#### `backend/services/land_lease_valuation.py`
Deterministic Valuation Engine for computing agricultural land lease prices in Karnataka.
It normalizes land area into Acres (`1 Hectare = 2.47105 Acres`, `40 Gunthas = 1 Acre`).
It applies Karnataka district baseline rates across 4 pricing tiers (Tier 1: ₹42k–48k/acre, Tier 2: ₹28k–35k/acre, Tier 3: ₹20k–24k/acre, Tier 4: ₹15k–18k/acre).
It applies multiplicative scoring for water availability (+35% / -20%), drip irrigation (+12%), 3-phase electricity (+15% / -12%), road access (+18% / -10%), fencing (+8%), pumps (+8%), storage (+10%), polyhouses (+25%), and crop suitability (+15%).
It evaluates input completeness to output a rule-based `HIGH`, `MODERATE`, or `LOW` confidence score with clear bulleted justifications.

#### `backend/services/mandi_service.py`
Service module for scraping and fetching live mandi market prices from official Karnataka portals.
It connects to `https://krama.karnataka.gov.in/Reports/Main_rep` to extract live commodity rates.
It parses raw HTML tables, regular expressions, and date headers to extract crop names, varieties, mandis, and min/max prices.
It normalizes commodity pricing data into structured dictionaries for database caching.
It provides fallback historical pricing data when live external government portals are unreachable.

---

### 🧰 `backend/utils/` — Helper Utilities

#### `backend/utils/__init__.py`
Package initialization file exporting backend utility helper functions.
It exposes AI completion wrappers, authentication helpers, validation functions, and weather parsers.
It simplifies utility function imports across service modules and route handlers.
It maintains clean helper sub-package boundaries.
It supports unified utility module resolution.

#### `backend/utils/ai.py`
Utility module providing direct integration with Groq Cloud AI completion APIs.
It manages HTTP POST requests to `https://api.groq.com/openai/v1/chat/completions` with JSON payload structuring.
It implements regex JSON extraction helpers (`_extract_json_object`) and user input sanitization (`_sanitize_user_input`).
It provides high-level AI helpers: `get_crop_suggestion`, `get_structured_crop_suggestion`, `get_disease_diagnosis`, and `generate_ai_crop_plan`.
It supports vision model calls for diagnosing crop leaf disease images.

#### `backend/utils/auth.py`
Security and authentication utility module handling password hashing and JWT token operations.
It implements password hashing and verification using `bcrypt` (`get_password_hash`, `verify_password`).
It generates signed JWT access tokens (`create_access_token`) with configurable expiration windows.
It implements the `get_current_user` FastAPI dependency, extracting JWTs from HTTP Bearer headers or `access_token` cookies.
It validates user and admin credentials against the database and enforces account approval status checks.

#### `backend/utils/crop_planner.py`
Utility module powering the interactive Crop Planner engine and stage calculator.
It maintains a built-in crop library (`PLANNER_CROP_LIBRARY`) containing growth stages, irrigation schedules, and fertilizer guidelines for major crops.
It computes date milestones based on sowing dates and land size.
It processes AI-generated custom crop plans and serializes growth stages into JSON structures.
It builds stage reminder alerts for dashboard notifications.

#### `backend/utils/mandi_prices.py`
Utility module handling local mandi price querying and database seeding functions.
It provides helper functions to search, filter, and format mandi price records by crop and district.
It formats currency figures and date strings for frontend dashboard display.
It supports automatic database seeding for default commodity prices.
It handles price range aggregation across different markets in a district.

#### `backend/utils/rate_limit.py`
Simple in-memory rate limiting utility module protecting sensitive endpoints from abuse.
It tracks client IP addresses and request counts within sliding time windows.
It raises `HTTPException(429, "Too Many Requests")` when request thresholds are exceeded.
It protects AI generation endpoints and login routes from brute-force or spam attacks.
It helps maintain server performance and API quota management.

#### `backend/utils/schemes.py`
Utility module managing government scheme data serialization and default seeding dataset.
It defines `DEFAULT_SCHEMES` dataset containing pre-configured national and Karnataka state agricultural schemes (e.g. PM-KISAN, Krishi Bhagya).
It provides `scheme_to_payload()` helper functions converting SQLAlchemy model instances into formatted JSON objects.
It handles list serialization for document requirements and step-by-step application instructions.
It supports automated database seeding during application startup.

#### `backend/utils/validation.py`
Validation helper utility module enforcing domain-specific data constraints.
It provides validation functions for Indian phone numbers (`is_valid_indian_phone`), soil pH levels (`is_valid_ph`), NPK values (`is_valid_npk`), and land size bounds.
It validates Karnataka district names (`is_valid_district`), seasons, soil types, and irrigation methods against allowed master lists.
It sanitizes text inputs to prevent script injection and invalid parameter values.
It ensures clean data before invoking backend services or persisting records.

#### `backend/utils/weather.py`
Weather service utility module integrating Open-Meteo geocoding and weather APIs.
It fetches real-time current weather, temperature, humidity, wind speed, and 7-day forecasts based on district names or GPS coordinates.
It converts district names into latitude/longitude coordinates using Open-Meteo Geocoding API.
It generates agricultural weather advisories based on rainfall forecasts and extreme temperature alerts.
It formats weather payload dictionaries for farmer dashboard cards and weather detail pages.

---

### 🗃️ `database/` — Database SQL Schemas & Migrations

#### `database/mysql/database.sql`
Original MySQL schema creation script representing local development database architecture.
It contains `CREATE TABLE` DDL statements for `users`, `admins`, `schemes`, `mandi_prices`, `crop_plans`, `ai_usage_history`, and `ads`.
It defines primary keys, foreign keys, auto-increment fields, unique constraints, and indexes.
It includes default seed data inserts for testing local XAMPP MySQL setups.
It serves as the original schema benchmark prior to PostgreSQL cloud migration.

#### `database/postgresql/database_postgresql.sql`
PostgreSQL-compatible DDL schema script optimized for Neon serverless PostgreSQL.
It translates MySQL data types to PostgreSQL equivalents (`VARCHAR`, `TEXT`, `BOOLEAN`, `TIMESTAMP WITH TIME ZONE`, `SERIAL`).
It defines foreign key constraints (`ON DELETE CASCADE`), indexes, and unique constraints.
It includes updated table definitions for `land_lease_estimates` and user profile extensions.
It allows manual schema bootstrapping or reference for PostgreSQL cloud deployment.

#### `database/migrations/migrate_mysql_to_neon.py`
Python migration script automating data migration from local XAMPP MySQL to Neon PostgreSQL.
It connects simultaneously to MySQL source database and Neon PostgreSQL destination database.
It derives `project_root` two levels up (`../..`) to import settings and models cleanly.
It extracts records table-by-table, transforms data types (booleans, timestamps, JSON text), and streams rows into PostgreSQL.
It handles sequence resetting and primary key index alignment following data transfer.

---

### 📚 `docs/` — Project Documentation Hub

#### `docs/DEPLOYMENT.md`
Comprehensive production deployment documentation guide for the CropCare platform.
It details step-by-step instructions for deploying the FastAPI backend to cloud platforms like Railway and configuring serverless PostgreSQL on Neon.
It outlines Vercel static asset deployment, domain configuration, CORS origin settings, and environment variable setup.
It includes troubleshooting steps for database migrations, SSL connection strings, and Ngrok tunneling setups.
It provides production hardening guidelines including security headers, rate limiting, and database connection pooling.

#### `docs/DESIGN.md`
Design system specifications and UI/UX design philosophy document for CropCare.
It establishes the primary emerald-green color palette, font hierarchies (Inter / Outfit / Roboto), glassmorphism components, and responsive grid layouts.
It details card padding rules, micro-animations, hover effects, icon usage guidelines, and mobile breakpoint behaviors.
It ensures design consistency across public landing pages, user dashboards, and administrative panels.
It serves as the UI benchmark for creating visual experiences that wow agricultural users.

#### `docs/PRODUCT.md`
Product roadmap and high-level feature specification document for the CropCare platform.
It describes target personas (farmers, landholders, agronomists, administrators) and core value propositions.
It outlines key product modules: AI Crop Recommendation, Disease Diagnosis, Mandi Price Tracking, Land Leasing Valuation, and Government Schemes.
It documents key metrics, user journeys, performance goals, and future expansion plans for precision farming.
It acts as the functional blueprint guiding architecture, feature scope, and user experience decisions.

#### `docs/PROJECT_SPECIFICATION.md`
Technical project requirements and system specification document detailing architectural constraints and data models.
It defines exact schema definitions, API endpoints, authentication flows, external API integrations, and database relations.
It specifies compliance requirements for Fast-API router design, Pydantic validation, SQLAlchemy ORM mappings, and error handling.
It details exact business logic rules for crop planning algorithms, weather data integration, and mandi pricing scrapers.
It provides developers and testing tools with authoritative technical guidance on expected system behavior.

#### `docs/README.md`
Primary repository documentation file introducing the CropCare precision agriculture platform.
It contains project highlights, architecture summaries, technology stack breakdowns, and setup instructions.
It guides users through cloning the repo, setting up virtual environments, installing `requirements.txt`, and launching `start.bat`.
It documents API keys, database connection setup, and quick commands for running unit tests.
It provides an overview of features, deployment links, and contributor guidelines for developers.

#### `docs/how_to_run.txt`
Simple plain-text quick-start guide for launching CropCare on Windows environments.
It provides step-by-step instructions for executing `start.bat` and `stop.bat` scripts.
It explains how the launcher automatically manages virtual environment setup, package installations, and Ngrok tunneling.
It informs users how to access the local web application at `http://127.0.0.1:8000` once started.
It offers quick troubleshooting hints for common PowerShell execution policy and port binding issues.

---

### 🎨 `frontend/` — Frontend View Templates, Static Assets & Uploads

#### `frontend/static/css/`
Static directory reserved for custom CSS stylesheets, utility classes, and custom font definitions.
It supports custom glassmorphism styles, color variables, animations, and print media overrides.
It works alongside Tailwind CSS CDN imports to deliver pixel-perfect visual styling.
It houses responsive theme customizations across public and user interfaces.

#### `frontend/static/js/`
Static directory for client-side JavaScript helper scripts, charts, and DOM manipulators.
It contains modules for interactive AJAX form handlers, dynamic modal toggles, and notification toasts.
It powers frontend charts, weather widgets, and live acreage conversion calculators.
It enhances user experience through smooth micro-animations and client-side validations.

#### `frontend/static/images/`
Static asset directory containing image resources, soil library references, and brand logos.
It contains high-resolution soil type illustration cards: `BLACK_COTTON_SOIL.png`, `RED_SOIL.png`, `LATERITE_SOIL.png`, `FOREST_SOIL.png`, `COASTAL_ALLUVIAL_SOIL.png`, and `REED_SANDY_LOAM_SOIL.png`.
It contains the official platform emblem: `logo.png` (and `logo_clean.png` with clean white background for PDF rendering).
It serves images displayed across user dashboards, soil library guides, and generated PDF reports.

#### `frontend/uploads/profiles/`
Local storage directory for user profile photos and avatar images.
It holds user-uploaded profile pictures named with unique user ID prefixes (e.g. `user_6_405db123b9.jpg`).
It is mounted by FastAPI under `/static/uploads` to maintain 100% backward-compatible public image URLs.
It provides avatar display across navigation headers, user profile forms, and admin account lists.

---

### 📄 `frontend/templates/` — Jinja2 HTML View Templates

#### `frontend/templates/about.html`
Public landing page template presenting CropCare's mission, vision, and technology stack.
It highlights precision agriculture features, team information, and platform capabilities.
It inherits from `base.html` using Jinja2 template inheritance.
It features responsive design elements, call-to-action buttons, and navigation footers.
It educates visitors on how AI and data analytics empower farming communities.

#### `frontend/templates/admin_login.html`
Dedicated administrative login portal template (`/admin/login`).
It provides a secure, styled login form for platform administrators.
It submits credentials via AJAX with custom anti-CSRF headers.
It features administrative branding, error alert callouts, and secure redirect handling.
It ensures separate authentication entry points for administrative users.

#### `frontend/templates/base.html`
Master Jinja2 base layout template extended by all public and authenticated pages.
It includes `<head>` metadata, SEO tags, Google Fonts, FontAwesome icons, Tailwind CSS, and global CSS stylesheets.
It defines master layout blocks: `{% block title %}`, `{% block sidebar %}`, `{% block content %}`, and `{% block scripts %}`.
It provides global navigation bars, responsive mobile sidebars, user profile dropdowns, and common modal dialogs.
It ensures consistent branding, navigation, and script execution across the application.

#### `frontend/templates/contact.html`
Public contact page template facilitating user inquiries, feedback, and support requests.
It presents contact forms, office location details, support email links, and helpline numbers.
It includes interactive form validation and success notification banners.
It allows farmers and partners to reach out to the CropCare administration team.
It inherits common header and footer navigation from `base.html`.

#### `frontend/templates/features.html`
Public feature showcase page detailing CropCare's precision farming modules.
It features interactive cards highlighting AI Crop Suggestion, Leaf Disease Diagnosis, Mandi Tracker, Land Leasing Valuation, and Government Schemes.
It includes visual icons, benefit breakdowns, and call-to-action links leading to signup/login.
It helps prospective users understand platform capabilities before registering.
It uses responsive Tailwind CSS grid layouts for modern visual presentation.

#### `frontend/templates/index.html`
Main public home landing page template (`/`) of the CropCare platform.
It features a hero banner with vibrant visuals, key value statistics, feature quick-links, and farmer testimonials.
It includes live call-to-action buttons directing users to register or explore public features.
It provides introductory overviews of AI diagnostic tools and real-time market price trackers.
It creates a strong first impression using rich aesthetics and dynamic animations.

#### `frontend/templates/login.html`
Farmer user login page template (`/auth/login`).
It provides a clean, user-friendly authentication form for returning farmers.
It includes email/phone input fields, password visibility toggles, and "Remember Me" options.
It handles AJAX authentication submission, error handling, and redirection to `/user/dashboard`.
It includes quick navigation links to the user registration page (`/auth/signup`).

#### `frontend/templates/signup.html`
Farmer user registration page template (`/auth/signup`).
It provides a sectioned registration form requesting name, email, phone number, state, district, land size, and password.
It performs client-side validation on phone numbers, passwords, and required fields.
It submits registration data to `/auth/signup` and redirects approved users to login.
It features responsive styling, inline help tooltips, and terms of service checkboxes.

---

### 🛡️ `frontend/templates/admin/` — Administrative Templates

#### `frontend/templates/admin/analytics.html`
Admin analytics dashboard view rendering platform usage statistics and trends (`/admin/analytics`).
It displays total registered farmers, active AI diagnoses, generated land reports, and scheme interaction totals.
It includes visual chart widgets, district distribution lists, and activity metrics.
It enables administrators to monitor platform growth and feature engagement.
It features clean administrative data tables and export action buttons.

#### `frontend/templates/admin/dashboard.html`
Primary administrative overview dashboard page (`/admin/dashboard`).
It provides quick action cards, system status indicators, pending user approval counts, and recent activity logs.
It features quick navigation shortcuts to user management, scheme updates, price tracking, and ad management.
It displays top platform metrics and security alerts for administrators.
It serves as the command center for platform operations.

#### `frontend/templates/admin/manage_admins.html`
Administrative user management page (`/admin/admins`).
It displays data tables listing all registered admin accounts, roles, and creation dates.
It provides modal forms for creating new administrator accounts and revoking admin access.
It includes security audit logs tracking administrative privilege changes.
It enforces super-admin privilege controls across account modification forms.

#### `frontend/templates/admin/manage_ads.html`
Promotional advertisement management interface (`/admin/ads`).
It allows administrators to create, edit, activate, deactivate, and delete dashboard promotional ads.
It provides image URL uploads, target web link configuration, and display priority controls.
It displays preview cards showing how ads will appear on farmer user dashboards.
It manages promotional content campaigns across the platform.

#### `frontend/templates/admin/manage_prices.html`
Mandi market price management and scraper control interface (`/admin/prices`).
It displays searchable tables of cached mandi commodity prices across Karnataka districts.
It provides manual price entry forms, bulk price updates, and trigger buttons for live mandi web scrapers.
It allows admins to edit min/max prices and correct commodity data anomalies.
It ensures market pricing accuracy across farmer price tracking tools.

#### `frontend/templates/admin/manage_schemes.html`
Government welfare scheme management interface (`/admin/schemes`).
It lists all national and state agricultural schemes with status toggles (`Active` / `Inactive`).
It provides rich modal forms for adding and editing scheme descriptions, eligibility rules, required documents, and official application links.
It allows administrators to target schemes to specific states or districts.
It keeps government subsidy data current and actionable for farmers.

#### `frontend/templates/admin/manage_users.html`
Farmer user account management interface (`/admin/users`).
It displays searchable, filterable data tables of all registered farmer accounts.
It provides one-click user account approval toggles (`Approve` / `Revoke`) and account deletion options.
It displays farmer profile details including location, land size, phone number, and registration date.
It gives administrators complete control over user account access and security.

---

### 🧩 `frontend/templates/partials/` — Reusable HTML Snippets

#### `frontend/templates/partials/common_modals.html`
Reusable Jinja2 template partial containing common UI modal dialogs.
It defines confirmation modals, image viewer lightboxes, and feedback alert popups.
It is included across base templates to avoid duplicating modal HTML structures.
It supports JavaScript-driven modal toggles and dynamic text injection.
It maintains uniform modal styling and keyboard escape handling across all pages.

#### `frontend/templates/partials/footer.html`
Reusable footer navigation partial included across all application views.
It contains platform copyright notices, quick navigation links, social media icons, and legal disclaimers.
It features responsive multi-column layouts adapting to mobile and desktop screens.
It displays developer attribution, version notes, and contact support links.
It provides consistent footer layout presentation across public and user pages.

---

### 👤 `frontend/templates/user/` — Farmer User Dashboard Templates

#### `frontend/templates/user/crop_planner.html`
Interactive seasonal crop planning interface for farmers (`/user/crop-planner`).
It allows farmers to select crops, input field size and sowing dates, or request Groq AI-generated crop plans.
It displays interactive timeline cards tracking growth stages, fertilizer milestones, and irrigation dates.
It features stage completion checkboxes, custom plan saving, and printable schedule exports.
It provides live notifications reminding farmers of upcoming field actions.

#### `frontend/templates/user/crop_recommendation.html`
AI-powered crop recommendation module (`/user/crop-recommendation`).
It allows farmers to input soil parameters (type, pH, NPK levels), location, season, and rainfall data or upload soil test reports.
It calls Groq AI to generate tailored crop suggestions with detailed suitability justifications.
It displays recommended crops, expected yield estimates, market demand scores, and risk advisories.
It saves recommendation queries to user AI history for future reference.

#### `frontend/templates/user/dashboard.html`
Primary farmer user dashboard page (`/user/dashboard`).
It presents a personalized farm overview: local weather card, active crop plan progress, price tracker summary, and scheme recommendations.
It features quick access shortcuts to all AI tools, land lease estimation, and profile settings.
It displays promotional agricultural ads and urgent seasonal advisories.
It serves as the daily home view for logged-in farmers.

#### `frontend/templates/user/disease_diagnosis.html`
AI crop disease diagnosis module (`/user/disease-diagnosis`).
It allows farmers to upload photos of diseased crop leaves or describe symptoms in text.
It sends images to Groq Vision AI models to identify plant diseases, severity levels, and causes.
It provides actionable treatment plans, organic remedies, recommended fungicides/pesticides, and preventive steps.
It archives past disease diagnoses in the farmer's history tab with downloadable summary reports.

#### `frontend/templates/user/gov_schemes.html`
Government welfare schemes discovery and search portal (`/user/gov-schemes`).
It allows farmers to browse national and Karnataka state subsidies, financial aid, and equipment schemes.
It provides search filters by scheme category, state, district, and beneficiary type.
It presents detailed scheme cards with benefit summaries, eligibility rules, document checklists, and direct official apply links.
It empowers farmers to claim government agricultural support programs.

#### `frontend/templates/user/input_suggestions.html`
Fertilizer, seed, and farming input recommendation module (`/user/input-suggestions`).
It allows farmers to select target crops, growth stages, and soil conditions to receive optimal input advice.
It calculates precise fertilizer dosages (NPK ratios, organic manure quantities, micro-nutrients) per acre.
It offers seed variety recommendations, pest control inputs, and application timing guides.
It helps farmers optimize input costs while maximizing crop productivity.

#### `frontend/templates/user/land_leasing.html`
Agricultural Land Lease Estimation & Valuation interface (`/user/land-leasing`).
It features a sectioned form capturing location, land area (with live Acre/Hectare/Guntha conversion), water source, electricity, road access, and infrastructure.
It displays deterministic annual valuation bounds (`Rs. X,XXX - Rs. Y,YYY / year`), monthly rates, per-acre rates, and confidence badges.
It presents primary price drivers grids, Groq AI strategic negotiation advice, and legal verification checklists.
It includes an **Estimation History** tab and a **Download PDF Report** button streaming branded valuation documents.

#### `frontend/templates/user/mandi_tracking.html`
Real-time agricultural market price tracker interface (`/user/mandi-tracking`).
It displays live mandi prices fetched from Karnataka government portals (`krama.karnataka.gov.in`).
It provides filter controls by crop name, district, and market mandi name.
It features price trend visualization cards, min/max price spreads, and daily price change indicators.
It includes an embedded live portal view button for direct government report access.

#### `frontend/templates/user/profile.html`
Farmer account profile management interface (`/user/profile`).
It allows farmers to update personal information, phone numbers, state, district, land size, and irrigation methods.
It provides profile photo upload forms supporting avatar preview and Cloudinary storage.
It includes security settings for password modification and session management.
It displays account verification status badges and registered farm parameters.

#### `frontend/templates/user/soil_library.html`
Educational soil classification and management guide (`/user/soil-library`).
It presents rich reference cards for major Indian soil types: Black Cotton, Red Loamy, Alluvial, Laterite, Forest, and Sandy Loam.
It details soil properties, water retention capabilities, pH ranges, nutrient profiles, and suitable crop lists.
It offers soil management tips, organic amendment advice, and erosion prevention strategies.
It serves as an agronomist knowledge hub helping farmers understand their land quality.

#### `frontend/templates/user/weather.html`
Comprehensive local weather advisory page (`/user/weather`).
It connects to Open-Meteo APIs to display real-time weather, temperature, humidity, wind speed, and rain probability for the farmer's district.
It features 7-day extended weather forecasts, hourly temperature charts, and precipitation metrics.
It generates agricultural weather advisories warning farmers of incoming heavy rainfall, frost, or heatwaves.
It helps farmers schedule sowing, spraying, and harvesting activities safely.

---

### ⚙️ `scripts/` — Process Management & Launcher Scripts

#### `scripts/launcher.ps1`
PowerShell automation script responsible for bootstrapping and orchestrating the CropCare application.
It derives `$ProjectDir` dynamically relative to `$PSScriptRoot\..` if not provided.
It verifies virtual environment existence, refreshes dependencies, and launches Uvicorn FastAPI background processes.
It records active Process IDs (PIDs) into `runtime/processes.json` and manages Ngrok public tunnel connections.
It opens default browsers to `http://127.0.0.1:8000` and displays terminal status summaries.

#### `scripts/start.bat`
Windows batch script executing `scripts/launcher.ps1` with bypassed execution policies.
It resolves project directory paths dynamically using `%~dp0..`.
It initializes application backend processes, environment dependencies, and browser windows.
It provides one-click startup capability for Windows development environments.
It handles error checking and status reporting during boot.

#### `scripts/stop.bat`
Windows batch script executing `scripts/stopper.ps1` with bypassed execution policies.
It resolves project directory paths dynamically using `%~dp0..`.
It terminates running Uvicorn server instances and Ngrok tunnels.
It ensures clean local process shutdown without leaving background locks.
It cleans up temporary runtime tracking files upon termination.

#### `scripts/stopper.ps1`
PowerShell automation script responsible for gracefully shutting down CropCare process trees.
It derives `$ProjectDir` dynamically relative to `$PSScriptRoot\..` if not provided.
It reads process tracking records from `runtime/processes.json` to identify active PIDs.
It sends termination signals to Uvicorn background workers, Ngrok processes, and child windows.
It verifies port 8000 release and cleans up temporary runtime lockfiles.

---

### 🧪 `tests/` — Automated Test Suite

#### `tests/test_land_leasing.py`
Automated unit and integration test suite for the Land Lease Estimation feature.
It tests `normalize_to_acres()` verifying Acre, Hectare (2.47105), and Guntha (0.025) calculations.
It tests `get_base_rate_for_district()` verifying Karnataka district baseline rate lookups.
It tests `calculate_land_valuation()` verifying multi-factor multipliers, price bounds, positive drivers, and confidence scores.
It tests `generate_land_lease_ai_assessment()` fallback responses and `generate_land_lease_pdf()` PDF byte generation using `frontend/static/images/logo.png`.
