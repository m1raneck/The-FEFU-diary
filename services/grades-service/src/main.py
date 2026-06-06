from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fefu_common.auth import AuthDependencies
from fefu_common.health import register_health_route

from . import database, models, schemas

app = FastAPI(title="Grades Service")
register_health_route(app, "grades-service")

auth_deps = AuthDependencies(models.User, database.get_db)
get_current_user = auth_deps.current_user_dependency()
get_teacher_role = auth_deps.teacher_role_dependency(get_current_user)


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
        existing.grade = grade.grade
        existing.comment = grade.comment
        db.commit()
        db.refresh(existing)
        return existing

    new_grade = models.Grade(
        student_id=grade.student_id,
        schedule_id=grade.schedule_id,
        grade=grade.grade,
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
    db_grade.student_id = grade.student_id
    db_grade.schedule_id = grade.schedule_id
    db_grade.grade = grade.grade
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
            existing.grade = item.grade
            existing.comment = item.comment
            created.append({"student_id": item.student_id, "action": "updated"})
        else:
            db.add(
                models.Grade(
                    student_id=item.student_id,
                    schedule_id=payload.schedule_id,
                    grade=item.grade,
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
