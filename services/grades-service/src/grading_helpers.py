from typing import Optional

from sqlalchemy.orm import Session

from fefu_common.grading import (
    ScaleRule,
    WeightedCategory,
    convert_score_to_grade,
)

from . import models, schemas

DEFAULT_SCALE_RULES = [
    schemas.GradeScaleRuleBase(min_points=0, max_points=40, final_grade=2),
    schemas.GradeScaleRuleBase(min_points=41, max_points=60, final_grade=3),
    schemas.GradeScaleRuleBase(min_points=61, max_points=80, final_grade=4),
    schemas.GradeScaleRuleBase(min_points=81, max_points=100, final_grade=5),
]


def load_scale_rules(db: Session, schedule_id: int) -> list[ScaleRule]:
    rows = (
        db.query(models.GradeScaleRule)
        .filter(models.GradeScaleRule.schedule_id == schedule_id)
        .order_by(models.GradeScaleRule.min_points)
        .all()
    )
    return [
        ScaleRule(float(r.min_points), float(r.max_points), r.final_grade)
        for r in rows
    ]


def load_categories(db: Session, schedule_id: int) -> list[WeightedCategory]:
    rows = (
        db.query(models.GradeCategory)
        .filter(models.GradeCategory.schedule_id == schedule_id)
        .all()
    )
    return [
        WeightedCategory(r.id, float(r.weight))
        for r in rows
    ]


def resolve_grade_value(
    db: Session,
    schedule_id: int,
    raw_score: Optional[float],
    grade: Optional[int],
    auto_convert: bool,
) -> tuple[Optional[int], Optional[float]]:
    """Определяет итоговую оценку и raw_score для сохранения."""
    if raw_score is None:
        return grade, None

    if auto_convert:
        rules = load_scale_rules(db, schedule_id)
        if rules:
            converted = convert_score_to_grade(float(raw_score), rules)
            if converted is not None:
                return converted, float(raw_score)

    return grade if grade is not None else int(round(raw_score)), float(raw_score)
