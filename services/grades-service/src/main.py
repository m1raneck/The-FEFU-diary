from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fefu_common.auth import AuthDependencies
from fefu_common.grading import ScoreEntry, calculate_final_grade, convert_score_to_grade
from fefu_common.health import register_health_route

from . import database, grading_helpers, models, schemas

app = FastAPI(title="Grades Service")
register_health_route(app, "grades-service", database.get_db)

auth_deps = AuthDependencies(models.User, database.get_db)
get_current_user = auth_deps.current_user_dependency()
get_teacher_role = auth_deps.teacher_role_dependency(get_current_user)


# ---------- Categories (weights) ----------


@app.get("/api/grades/categories", response_model=List[schemas.GradeCategoryResponse])
def list_categories(
    schedule_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.GradeCategory)
        .filter(models.GradeCategory.schedule_id == schedule_id)
        .order_by(models.GradeCategory.code)
        .all()
    )
    if not rows:
        return [
            schemas.GradeCategoryResponse(
                id=0,
                schedule_id=schedule_id,
                **cat.model_dump(),
            )
            for cat in grading_helpers.DEFAULT_CATEGORIES
        ]

    if grading_helpers.categories_need_default_weights(rows):
        for row in rows:
            row.weight = grading_helpers.DEFAULT_CATEGORY_WEIGHT
        db.commit()
        for row in rows:
            db.refresh(row)

    return rows


@app.put("/api/grades/categories", response_model=List[schemas.GradeCategoryResponse])
def set_categories(
    payload: schemas.GradeCategorySetRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db.query(models.GradeCategory).filter(
        models.GradeCategory.schedule_id == payload.schedule_id
    ).delete()

    created = []
    for cat in payload.categories:
        row = models.GradeCategory(
            schedule_id=payload.schedule_id,
            code=cat.code,
            name=cat.name,
            weight=cat.weight,
        )
        db.add(row)
        created.append(row)

    db.commit()
    for row in created:
        db.refresh(row)
    return created


# ---------- Column types (ДЗ / КР / ДОП per date) ----------


@app.get("/api/grades/columns", response_model=List[schemas.GradeColumnSettingResponse])
def list_column_settings(
    schedule_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    return (
        db.query(models.GradeColumnSetting)
        .filter(models.GradeColumnSetting.schedule_id == schedule_id)
        .order_by(models.GradeColumnSetting.grade_date)
        .all()
    )


@app.put("/api/grades/columns", response_model=List[schemas.GradeColumnSettingResponse])
def set_column_settings(
    payload: schemas.GradeColumnSetRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db.query(models.GradeColumnSetting).filter(
        models.GradeColumnSetting.schedule_id == payload.schedule_id
    ).delete()

    created = []
    for col in payload.columns:
        row = models.GradeColumnSetting(
            schedule_id=payload.schedule_id,
            grade_date=col.grade_date,
            column_type=col.column_type,
        )
        db.add(row)
        created.append(row)

    db.commit()
    for row in created:
        db.refresh(row)
    return created


@app.post(
    "/api/grades/categories",
    response_model=schemas.GradeCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: schemas.GradeCategoryCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    category = models.GradeCategory(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category code already exists for this schedule") from e


@app.put("/api/grades/categories/{category_id}", response_model=schemas.GradeCategoryResponse)
def update_category(
    category_id: int,
    payload: schemas.GradeCategoryUpdate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    category = db.query(models.GradeCategory).filter(models.GradeCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/grades/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    category = db.query(models.GradeCategory).filter(models.GradeCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"status": "success", "message": "Category deleted"}


# ---------- Scale rules (points → grade) ----------


@app.get("/api/grades/scale", response_model=List[schemas.GradeScaleRuleResponse])
def get_scale_rules(
    schedule_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    rules = (
        db.query(models.GradeScaleRule)
        .filter(models.GradeScaleRule.schedule_id == schedule_id)
        .order_by(models.GradeScaleRule.min_points)
        .all()
    )
    if not rules:
        return [
            schemas.GradeScaleRuleResponse(id=0, schedule_id=schedule_id, **r.model_dump())
            for r in grading_helpers.DEFAULT_SCALE_RULES
        ]
    return rules


@app.put("/api/grades/scale", response_model=List[schemas.GradeScaleRuleResponse])
def set_scale_rules(
    payload: schemas.GradeScaleSetRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    for rule in payload.rules:
        if rule.min_points > rule.max_points:
            raise HTTPException(status_code=400, detail="min_points must be <= max_points")

    db.query(models.GradeScaleRule).filter(
        models.GradeScaleRule.schedule_id == payload.schedule_id
    ).delete()

    created = []
    for rule in payload.rules:
        row = models.GradeScaleRule(
            schedule_id=payload.schedule_id,
            min_points=rule.min_points,
            max_points=rule.max_points,
            final_grade=rule.final_grade,
        )
        db.add(row)
        created.append(row)

    db.commit()
    for row in created:
        db.refresh(row)
    return created


@app.post("/api/grades/convert", response_model=schemas.ConvertScoreResponse)
def convert_score(
    payload: schemas.ConvertScoreRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    rules = grading_helpers.load_scale_rules(db, payload.schedule_id)
    if not rules:
        raise HTTPException(status_code=404, detail="Scale not configured for this schedule")
    final_grade = convert_score_to_grade(payload.raw_score, rules)
    return schemas.ConvertScoreResponse(
        raw_score=payload.raw_score,
        final_grade=final_grade,
        matched=final_grade is not None,
    )


@app.post("/api/grades/calculate-final", response_model=schemas.CalculateFinalResponse)
def calculate_final(
    payload: schemas.CalculateFinalRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    categories = grading_helpers.load_categories(db, payload.schedule_id)
    scale_rules = grading_helpers.load_scale_rules(db, payload.schedule_id)
    entries = [ScoreEntry(e.category_id, e.raw_score) for e in payload.entries]
    result = calculate_final_grade(entries, categories, scale_rules)
    return schemas.CalculateFinalResponse(**result)


# ---------- Grades CRUD ----------


@app.get("/api/grades", response_model=List[schemas.GradeResponse])
def get_grades(
    student_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    profiles = auth_deps.get_profile_ids(db, current_user.id)

    if profiles["student_id"]:
        query = db.query(models.Grade).filter(models.Grade.student_id == profiles["student_id"])
        if schedule_id:
            query = query.filter(models.Grade.schedule_id == schedule_id)
        return query.all()

    if profiles["teacher_id"]:
        query = db.query(models.Grade)
        if student_id:
            query = query.filter(models.Grade.student_id == student_id)
        if schedule_id:
            query = query.filter(models.Grade.schedule_id == schedule_id)
        return query.all()

    raise HTTPException(status_code=403, detail="No role assigned")


@app.post("/api/grades", response_model=schemas.GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(
    grade: schemas.GradeCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    grade_date = grade.grade_date or date.today()
    final_grade, raw_score = grading_helpers.resolve_grade_value(
        db,
        grade.schedule_id,
        grade.raw_score,
        grade.grade,
        grade.auto_convert,
    )

    existing = (
        db.query(models.Grade)
        .filter(
            models.Grade.student_id == grade.student_id,
            models.Grade.schedule_id == grade.schedule_id,
            models.Grade.grade_date == grade_date,
        )
        .first()
    )
    if existing:
        existing.grade = final_grade
        existing.raw_score = raw_score
        existing.category_id = grade.category_id
        existing.comment = grade.comment
        db.commit()
        db.refresh(existing)
        return existing

    new_grade = models.Grade(
        student_id=grade.student_id,
        schedule_id=grade.schedule_id,
        category_id=grade.category_id,
        grade=final_grade,
        raw_score=raw_score,
        grade_date=grade_date,
        comment=grade.comment,
    )
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade


@app.put("/api/grades/{grade_id}", response_model=schemas.GradeResponse)
def update_grade(
    grade_id: int,
    grade: schemas.GradeCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    final_grade, raw_score = grading_helpers.resolve_grade_value(
        db,
        grade.schedule_id,
        grade.raw_score,
        grade.grade,
        grade.auto_convert,
    )

    db_grade.student_id = grade.student_id
    db_grade.schedule_id = grade.schedule_id
    db_grade.category_id = grade.category_id
    db_grade.grade = final_grade
    db_grade.raw_score = raw_score
    db_grade.comment = grade.comment
    if grade.grade_date:
        db_grade.grade_date = grade.grade_date
    db.commit()
    db.refresh(db_grade)
    return db_grade


@app.delete("/api/grades/{grade_id}")
def delete_grade(
    grade_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    db.delete(db_grade)
    db.commit()
    return {"status": "success", "message": "Grade deleted"}


@app.post("/api/grades/bulk")
def bulk_create_grades(
    payload: schemas.BulkGradeRequest,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    created = []
    for item in payload.grades:
        final_grade, raw_score = grading_helpers.resolve_grade_value(
            db,
            payload.schedule_id,
            item.raw_score,
            item.grade,
            item.auto_convert,
        )
        existing = (
            db.query(models.Grade)
            .filter(
                models.Grade.student_id == item.student_id,
                models.Grade.schedule_id == payload.schedule_id,
                models.Grade.grade_date == payload.grade_date,
            )
            .first()
        )
        if existing:
            existing.grade = final_grade
            existing.raw_score = raw_score
            existing.category_id = item.category_id
            existing.comment = item.comment
            created.append({"student_id": item.student_id, "action": "updated"})
        else:
            db.add(
                models.Grade(
                    student_id=item.student_id,
                    schedule_id=payload.schedule_id,
                    category_id=item.category_id,
                    grade=final_grade,
                    raw_score=raw_score,
                    grade_date=payload.grade_date,
                    comment=item.comment,
                )
            )
            created.append({"student_id": item.student_id, "action": "created"})
    try:
        db.commit()
        return {"status": "success", "data": created, "message": f"Processed {len(created)} grades"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid grade data") from e
