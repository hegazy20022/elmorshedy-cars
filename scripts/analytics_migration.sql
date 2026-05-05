-- 1. جدول لتخزين التقارير التحليلية الشهرية اللي الأيجنت هيكتبها
CREATE TABLE IF NOT EXISTS analytics_reports (
    report_id SERIAL PRIMARY KEY,
    report_month DATE NOT NULL, -- أول يوم في الشهر (مثلاً 2024-05-01)
    report_text TEXT NOT NULL,  -- التقرير المكتوب بالعامية المصرية
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics_json JSONB DEFAULT '{}'::jsonb -- الأرقام اللي التقرير اتبنى عليها
);

-- 2. إضافة إندكس على الـ metadata في جدول الرسائل لتسريع الكويريز بتاعة التحليلات
CREATE INDEX IF NOT EXISTS idx_messages_metadata_gin ON messages USING GIN (metadata);

-- 3. جدول لتتبع اهتمامات العملاء بالعربيات بشكل أدق
CREATE TABLE IF NOT EXISTS car_interests (
    interest_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE,
    car_id INT REFERENCES cars(car_id) ON DELETE CASCADE,
    interest_type TEXT DEFAULT 'view', -- 'view', 'ask', 'book'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_car_interests_car_id ON car_interests(car_id);
CREATE INDEX IF NOT EXISTS idx_car_interests_created_at ON car_interests(created_at);
