CREATE TABLE IF NOT EXISTS lesson_comments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
    lesson_date DATE NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, schedule_id, lesson_date)
);

CREATE INDEX IF NOT EXISTS idx_lesson_comments_schedule_id ON lesson_comments(schedule_id);
CREATE INDEX IF NOT EXISTS idx_lesson_comments_student_id ON lesson_comments(student_id);

INSERT INTO lesson_comments (student_id, schedule_id, lesson_date, comment)
SELECT student_id, schedule_id, grade_date, comment
FROM grades
WHERE comment IS NOT NULL AND TRIM(comment) <> ''
ON CONFLICT (student_id, schedule_id, lesson_date) DO NOTHING;
