-- CropCare PostgreSQL Schema (Neon Cloud Compatible)
-- Created for PostgreSQL 14+ / Neon Serverless PostgreSQL

-- 1. Table structure for table `users`
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    state VARCHAR(100) DEFAULT 'Karnataka',
    district VARCHAR(100) NULL,
    phone_number VARCHAR(10) UNIQUE NULL,
    land_size DOUBLE PRECISION NULL,
    irrigation_type VARCHAR(100) NULL,
    profile_photo VARCHAR(500) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users (phone_number);

-- 2. Table structure for table `admins`
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_approved BOOLEAN NOT NULL DEFAULT TRUE,
    profile_photo VARCHAR(500) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX IF NOT EXISTS ix_admins_email ON admins (email);

-- 3. Table structure for table `ads`
CREATE TABLE IF NOT EXISTS ads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    image_url VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

-- 4. Table structure for table `schemes`
CREATE TABLE IF NOT EXISTS schemes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'national',
    beneficiary VARCHAR(100) NULL,
    benefits TEXT NULL,
    eligibility TEXT NULL,
    documents_required TEXT NULL,
    steps_to_apply TEXT NULL,
    duration VARCHAR(255) NULL,
    official_link VARCHAR(500) NULL,
    icon VARCHAR(100) DEFAULT 'fas fa-hand-holding-heart',
    state VARCHAR(100) NULL,
    district VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

-- 5. Table structure for table `crop_plans`
CREATE TABLE IF NOT EXISTS crop_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crop VARCHAR(100) NOT NULL,
    planting_date DATE NOT NULL,
    harvest_date DATE NOT NULL,
    duration_days INTEGER NOT NULL,
    reminders_json TEXT NULL,
    stages_json TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE INDEX IF NOT EXISTS ix_crop_plans_user_id ON crop_plans (user_id);

-- 6. Table structure for table `mandi_prices`
CREATE TABLE IF NOT EXISTS mandi_prices (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(120) NOT NULL,
    variety VARCHAR(120) NULL,
    grade VARCHAR(120) NULL,
    district VARCHAR(120) NOT NULL,
    mandi_name VARCHAR(180) NOT NULL,
    arrival DOUBLE PRECISION NULL,
    unit VARCHAR(50) NULL,
    price_per_quintal DOUBLE PRECISION NOT NULL,
    min_price DOUBLE PRECISION NULL,
    max_price DOUBLE PRECISION NULL,
    price_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'KRAMA' NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT uq_mandi_crop_market_week UNIQUE (crop_name, district, mandi_name, price_date)
);

CREATE INDEX IF NOT EXISTS ix_mandi_prices_id ON mandi_prices (id);

-- 7. Table structure for table `district_rainfall`
CREATE TABLE IF NOT EXISTS district_rainfall (
    id SERIAL PRIMARY KEY,
    district VARCHAR(100) NOT NULL UNIQUE,
    labels_json TEXT NULL,
    rainfall_json TEXT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_district_rainfall_district ON district_rainfall (district);

-- 8. Table structure for table `ai_usage_history`
CREATE TABLE IF NOT EXISTS ai_usage_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_type VARCHAR(100) NOT NULL,
    input_payload TEXT NULL,
    output_payload TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_ai_usage_history_user_id ON ai_usage_history (user_id);
CREATE INDEX IF NOT EXISTS ix_ai_usage_history_feature_type ON ai_usage_history (feature_type);
