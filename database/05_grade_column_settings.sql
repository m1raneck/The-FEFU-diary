CREATE TABLE IF NOT EXISTS grade_column_settings (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
    grade_date DATE NOT NULL,
    column_type VARCHAR(10) NOT NULL,
    UNIQUE (schedule_id, grade_date)
);

CREATE INDEX IF NOT EXISTS idx_grade_column_settings_schedule ON grade_column_settings(schedule_id);
