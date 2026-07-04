-- CropCare MySQL schema
-- Import this file in phpMyAdmin after selecting/creating `cropcare_db`.
-- CREATE DATABASE IF NOT EXISTS cropcare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE cropcare_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    state VARCHAR(100) DEFAULT 'Karnataka',
    district VARCHAR(100) NULL,
    land_size FLOAT NULL,
    irrigation_type VARCHAR(100) NULL,
    profile_photo VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    image_url VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    icon VARCHAR(100) NULL,
    state VARCHAR(100) NULL,
    district VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crop_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    crop VARCHAR(100) NOT NULL,
    planting_date DATE NOT NULL,
    harvest_date DATE NOT NULL,
    duration_days INT NOT NULL,
    reminders_json TEXT NULL,
    stages_json LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crop_plans_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS mandi_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(120) NOT NULL,
    district VARCHAR(120) NOT NULL,
    mandi_name VARCHAR(180) NOT NULL,
    price_per_quintal FLOAT NOT NULL,
    min_price FLOAT NULL,
    max_price FLOAT NULL,
    price_date DATE NOT NULL,
    last_updated DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_mandi_crop_market_week (crop_name, district, mandi_name, price_date)
);

CREATE TABLE IF NOT EXISTS district_rainfall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(100) NOT NULL UNIQUE,
    labels_json TEXT NULL,
    rainfall_json TEXT NULL,
    fetched_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_district_rainfall_district (district)
);

CREATE TABLE IF NOT EXISTS ai_usage_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    feature_type VARCHAR(100) NOT NULL,
    input_payload TEXT NULL,
    output_payload TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ai_history_user_feature (user_id, feature_type),
    CONSTRAINT fk_ai_history_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS ai_usage_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    feature_type VARCHAR(100) NOT NULL,
    input_payload TEXT NULL,
    output_payload TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ai_history_user_feature (user_id, feature_type),
    CONSTRAINT fk_ai_history_user FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Seed admin row (for consistency in users table).
-- NOTE: Replace password_hash with a real bcrypt hash if you plan DB-based login for this row.
INSERT INTO users (name, email, password_hash, role, is_approved)
VALUES ('Admin User', 'admin@cropcare.com', '$2a$12$gL0t3BogaBEplHGf8hFy2uEWq1dBXJYl7Q1LjFL3jMVPJqJ5dX.1e', 'admin', TRUE)
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- Seed sample users.
-- NOTE: Replace password_hash values with real bcrypt hashes before testing user login.
INSERT INTO users (name, email, password_hash, district, land_size, irrigation_type, is_approved) VALUES
('Rajesh Kumar', 'rajesh@example.com', '$2a$12$fsHPLCqeqiyiEpMaCfXtNeGlNa6eHsSWbXvRZs0/6iGOFFeIFKvZ2', 'Bagalkot', 2.5, 'Canal/Borewell', TRUE),
('Priya Sharma', 'priya@example.com', '$2a$12$w7c8q9r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7', 'Mysuru', 1.8, 'Drip', TRUE),
('Amit Patel', 'amit@example.com', '$2a$12$z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0f9e8d7c6b5a4z3y2x1w0v9u8t7s6r5q4p3o2n1m0l9k8j7i6h5g4f3e2d1c0b9a8z7y6x5w4v3u2t1s0r9q8p7o6n5m4l3k2j1i0h9g8f7e6d5c4b3a2z1y0x9w8v7u6t5s4r3q2p1o0n9m8l7k6j5i4h3g2f1e0d9c8b7a6z5y4x3w2v1u0t9s8r7q6p5o4n3m2l1k0j9i8h7g6f5e4d3c2b1a0', 'Belagavi', 5.0, 'Sprinkler', FALSE),
('Sunita Devi', 'sunita@example.com', '$2a$12$a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7', 'Bihar', 1.2, 'Rain-fed', TRUE)
ON DUPLICATE KEY UPDATE email = VALUES(email);

INSERT INTO ads (title, content, is_active) VALUES
('Premium Fertilizer Offer', 'Get 20% discount on premium organic fertilizers this month!', TRUE);

INSERT INTO schemes (title, description, type, beneficiary, benefits, eligibility, documents_required, steps_to_apply, duration, official_link, icon, state, district, is_active) VALUES
('PM-KISAN Samman Nidhi', 'Income support scheme for eligible farmer families through direct benefit transfer.', 'national', 'small', 'Rs. 6,000 per year in three installments.', 'Landholding farmer families, subject to central government exclusions.', '["Aadhaar card", "Bank account details", "Land records"]', '["Visit the PM-KISAN portal or nearest agriculture office.", "Submit Aadhaar, bank details, and land ownership records.", "Complete beneficiary verification.", "Track payment status through the official portal."]', 'Ongoing', 'https://pmkisan.gov.in/', 'fas fa-rupee-sign', NULL, NULL, TRUE),
('Pradhan Mantri Fasal Bima Yojana', 'Crop insurance support for notified crops against yield losses and localized risks.', 'national', 'general', 'Insurance coverage for crop loss subject to notified crop and season rules.', 'Farmers cultivating notified crops in notified areas.', '["Aadhaar card", "Bank passbook", "Land record or cultivation proof", "Sowing details"]', '["Check whether your crop and area are notified for the season.", "Apply through the official portal, bank, or Common Service Center.", "Submit land and sowing details before the deadline.", "Report losses within the prescribed timeline if crop damage occurs."]', 'Seasonal enrollment', 'https://pmfby.gov.in/', 'fas fa-shield-alt', NULL, NULL, TRUE),
('Soil Health Card Scheme', 'Soil testing program that helps farmers improve nutrient management and crop planning.', 'national', 'general', 'Field-specific soil nutrient recommendations and soil health reporting.', 'Farmers seeking soil testing support through agriculture department channels.', '["Land details", "Farmer ID proof", "Soil sample information"]', '["Contact the local agriculture office or soil testing center.", "Submit the soil sample following the recommended method.", "Register the sample with land and farmer details.", "Collect the soil health report and follow nutrient guidance."]', 'Periodic testing support', 'https://soilhealth.dac.gov.in/', 'fas fa-vial', NULL, NULL, TRUE),
('Krishi Bhagya', 'Karnataka support program focused on farm ponds and rainwater conservation for dryland farmers.', 'state', 'small', 'Support for water harvesting structures and related conservation components.', 'Eligible Karnataka farmers, especially in rain-fed and dryland areas, subject to state norms.', '["Aadhaar card", "RTC or land records", "Bank account details", "Passport-size photo"]', '["Visit the local Raitha Samparka Kendra or Karnataka agriculture office.", "Submit land and identity documents for scheme screening.", "Complete field verification by department staff.", "Receive approval and proceed as per department guidance."]', 'State program cycle', 'https://raitamitra.karnataka.gov.in/', 'fas fa-water', 'Karnataka', NULL, TRUE),
('Karnataka Farm Mechanization Support', 'State assistance for eligible farmers adopting approved agricultural machinery and equipment.', 'state', 'general', 'Subsidy support on approved implements and mechanization components as per state norms.', 'Eligible farmers in Karnataka applying through the agriculture department process.', '["Aadhaar card", "Land records", "Quotation or invoice", "Bank account details"]', '["Review the approved machinery list and subsidy norms.", "Apply through the notified Karnataka agriculture portal or office.", "Upload or submit land, identity, and equipment documents.", "Complete verification and claim processing after approval."]', 'Annual or notification-based', 'https://raitamitra.karnataka.gov.in/', 'fas fa-tractor', 'Karnataka', NULL, TRUE);
