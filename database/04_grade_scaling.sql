-- Категории оценок с весовыми коэффициентами (ДЗ, КР, тест и т.д.)
CREATE TABLE IF NOT EXISTS grade_categories (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    weight NUMERIC(6, 4) NOT NULL CHECK (weight > 0),
    max_points NUMERIC(10, 2) NOT NULL DEFAULT 100 CHECK (max_points > 0),
    UNIQUE (schedule_id, code)
);

-- Шкала перевода баллов в оценку (например 5–10 баллов → 3)
CREATE TABLE IF NOT EXISTS grade_scale_rules (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
    min_points NUMERIC(10, 2) NOT NULL,
    max_points NUMERIC(10, 2) NOT NULL,
    final_grade INTEGER NOT NULL CHECK (final_grade BETWEEN 2 AND 5),
    CHECK (min_points <= max_points)
);

CREATE INDEX IF NOT EXISTS idx_grade_categories_schedule ON grade_categories(schedule_id);
CREATE INDEX IF NOT EXISTS idx_grade_scale_rules_schedule ON grade_scale_rules(schedule_id);

ALTER TABLE grades ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES grade_categories(id) ON DELETE SET NULL;
ALTER TABLE grades ADD COLUMN IF NOT EXISTS raw_score NUMERIC(10, 2);

CREATE INDEX IF NOT EXISTS idx_grades_category_id ON grades(category_id);
