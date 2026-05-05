

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS car_financing_options CASCADE;
DROP TABLE IF EXISTS cache_entries CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversation_state CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS conversation_summaries CASCADE;
DROP TABLE IF EXISTS sold_cars CASCADE;
DROP TABLE IF EXISTS purchase_requests CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS business_info CASCADE;
DROP TABLE IF EXISTS cars CASCADE;

CREATE TABLE cars (
    car_id SERIAL PRIMARY KEY,
    car_name TEXT NOT NULL,
    brand TEXT,
    model TEXT,
    model_year INT,
    color TEXT,
    description TEXT,
    license_status TEXT,
    cash_price NUMERIC(12,2),
    installment_price NUMERIC(12,2),
    class_level TEXT,

    transmission TEXT,
    fuel_type TEXT,
    body_type TEXT,
    engine_cc INT,
    usage_tags JSONB DEFAULT '[]'::jsonb,
    city_friendly BOOLEAN DEFAULT FALSE,
    family_friendly BOOLEAN DEFAULT FALSE,
    fuel_economy_level TEXT,
    mileage INT,
    paint_status TEXT,

    is_sold BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE car_financing_options (
    financing_id SERIAL PRIMARY KEY,
    car_id INT NOT NULL REFERENCES cars(car_id) ON DELETE CASCADE,
    down_payment NUMERIC(12,2),
    installment_months INT,
    installment_value NUMERIC(12,2),
    total_price NUMERIC(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    telegram_user_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    address TEXT,
    username TEXT,
    preferred_car_id INT REFERENCES cars(car_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sold_cars (
    sale_id SERIAL PRIMARY KEY,
    car_id INT NOT NULL REFERENCES cars(car_id) ON DELETE RESTRICT,
    customer_id INT REFERENCES customers(customer_id) ON DELETE SET NULL,
    buyer_name TEXT,
    buyer_phone TEXT,
    buyer_address TEXT,
    cash_price NUMERIC(12,2),
    down_payment NUMERIC(12,2),
    remaining_amount NUMERIC(12,2),
    installment_months INT,
    installment_end_date DATE,
    installment_value NUMERIC(12,2),
    sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_requests (
    request_id SERIAL PRIMARY KEY,
    seller_name TEXT,
    seller_phone TEXT,
    seller_address TEXT,
    car_name TEXT,
    brand TEXT,
    model TEXT,
    model_year INT,
    color TEXT,
    license_status TEXT,
    description TEXT,
    asking_price NUMERIC(12,2),
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business_info (
    info_id SERIAL PRIMARY KEY,
    info_key TEXT UNIQUE NOT NULL,
    info_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_summaries (
    summary_id SERIAL PRIMARY KEY,
    week_start DATE,
    summary TEXT,
    top_questions TEXT,
    customer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    car_id INT NOT NULL REFERENCES cars(car_id) ON DELETE RESTRICT,
    customer_id INT REFERENCES customers(customer_id) ON DELETE SET NULL,
    customer_name TEXT,
    customer_phone TEXT,
    customer_address TEXT,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    day_name TEXT,
    booking_status TEXT DEFAULT 'confirmed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_state (
    telegram_user_id TEXT PRIMARY KEY,
    mode TEXT DEFAULT 'AI',
    current_intent TEXT,
    current_step TEXT,
    selected_car_id INT REFERENCES cars(car_id) ON DELETE SET NULL,
    context JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    customer_id INT REFERENCES customers(customer_id) ON DELETE SET NULL,
    sender_type TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    message_text TEXT,
    detected_intent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cache_entries (
    cache_id SERIAL PRIMARY KEY,
    car_id INT REFERENCES cars(car_id) ON DELETE CASCADE,
    intent TEXT NOT NULL,
    raw_question TEXT,
    normalized_question TEXT,
    cache_key TEXT UNIQUE NOT NULL,
    repeat_count INT DEFAULT 1,
    cached_answer TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    last_hit_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    actor_type TEXT NOT NULL,
    actor_id TEXT,
    action_name TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cars_name ON cars(car_name);
CREATE INDEX idx_cars_brand ON cars(brand);
CREATE INDEX idx_cars_model ON cars(model);
CREATE INDEX idx_cars_model_year ON cars(model_year);
CREATE INDEX idx_cars_available ON cars(is_available);
CREATE INDEX idx_cars_price ON cars(cash_price);
CREATE INDEX idx_cars_transmission ON cars(transmission);
CREATE INDEX idx_cars_fuel_type ON cars(fuel_type);
CREATE INDEX idx_cars_body_type ON cars(body_type);
CREATE INDEX idx_cars_city_friendly ON cars(city_friendly);
CREATE INDEX idx_cars_family_friendly ON cars(family_friendly);
CREATE INDEX idx_cars_fuel_economy_level ON cars(fuel_economy_level);
CREATE INDEX idx_cars_mileage ON cars(mileage);
CREATE INDEX idx_cars_paint_status ON cars(paint_status);
CREATE INDEX idx_cars_usage_tags ON cars USING GIN (usage_tags);

CREATE INDEX idx_car_financing_car_id ON car_financing_options(car_id);

CREATE INDEX idx_customers_telegram_user_id ON customers(telegram_user_id);
CREATE INDEX idx_customers_preferred_car_id ON customers(preferred_car_id);

CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_time ON bookings(booking_time);
CREATE INDEX idx_bookings_car_id ON bookings(car_id);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);

CREATE INDEX idx_messages_user ON messages(telegram_user_id);
CREATE INDEX idx_messages_customer_id ON messages(customer_id);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
CREATE INDEX idx_messages_detected_intent ON messages(detected_intent);

CREATE INDEX idx_conversation_state_mode ON conversation_state(mode);
CREATE INDEX idx_conversation_state_selected_car_id ON conversation_state(selected_car_id);

CREATE INDEX idx_cache_entries_car_id ON cache_entries(car_id);
CREATE INDEX idx_cache_entries_intent ON cache_entries(intent);
CREATE INDEX idx_cache_entries_active ON cache_entries(is_active);

CREATE INDEX idx_business_info_value ON business_info USING GIN (info_value);
CREATE INDEX idx_messages_metadata ON messages USING GIN (metadata);
CREATE INDEX idx_conversation_state_context ON conversation_state USING GIN (context);
CREATE INDEX idx_audit_logs_details ON audit_logs USING GIN (details);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cars_updated_at
BEFORE UPDATE ON cars
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_car_financing_options_updated_at
BEFORE UPDATE ON car_financing_options
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_purchase_requests_updated_at
BEFORE UPDATE ON purchase_requests
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_business_info_updated_at
BEFORE UPDATE ON business_info
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_conversation_state_updated_at
BEFORE UPDATE ON conversation_state
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_cache_entries_updated_at
BEFORE UPDATE ON cache_entries
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO business_info (info_key, info_value) VALUES
('bot_enabled', '{"value": true}'),
('booking_settings', '{
  "working_days": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
  "start_time": "10:00",
  "end_time": "18:00",
  "slot_duration_minutes": 60
}'),
('cache_settings', '{
  "repeat_threshold": 3,
  "ttl_hours": 24
}'),
('business_contact', '{
  "phone": "",
  "address": "",
  "telegram_owner_id": ""
}');
