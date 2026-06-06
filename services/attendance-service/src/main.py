from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from fefu_common.auth import AuthDependencies
from fefu_common.health import register_health_route

from . import database, models, schemas

app = FastAPI(title="Attendance Service")
register_health_route(app, "attendance-service")

auth_deps = AuthDependencies(models.User, database.get_db)
get_current_user = auth_deps.current_user_dependency()
get_teacher_role = auth_deps.teacher_role_dependency(get_current_user)


@app.get("/api/attendance", response_model=list[schemas.AttendanceResponse])
def get_attendance(
    student_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    profiles = auth_deps.get_profile_ids(db, current_user.id)

    if profiles["student_id"]:
        query = db.query(models.Attendance).filter(
            models.Attendance.student_id == profiles["student_id"]
        )
        if schedule_id:
            query = query.filter(models.Attendance.schedule_id == schedule_id)
        if attendance_date:
            query = query.filter(models.Attendance.date == attendance_date)
        return query.all()

    if profiles["teacher_id"]:
        query = db.query(models.Attendance)
        if student_id:
            query = query.filter(models.Attendance.student_id == student_id)
        if schedule_id:
            query = query.filter(models.Attendance.schedule_id == schedule_id)
        if attendance_date:
            query = query.filter(models.Attendance.date == attendance_date)
        return query.all()

    raise HTTPException(status_code=403, detail="No role assigned")


@app.post("/api/attendance", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    att: schemas.AttendanceCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    att_date = att.record_date or date.today()
    existing = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == att.student_id,
            models.Attendance.schedule_id == att.schedule_id,
            models.Attendance.date == att_date,
        )
        .first()
    )
    if existing:
        existing.status = att.status
        existing.comment = att.comment
        db.commit()
        db.refresh(existing)
        return existing

    new_att = models.Attendance(
        student_id=att.student_id,
        schedule_id=att.schedule_id,
        status=att.status,
        date=att_date,
        comment=att.comment,
    )
    db.add(new_att)
    db.commit()
    db.refresh(new_att)
    return new_att


@app.put("/api/attendance/{attendance_id}", response_model=schemas.AttendanceResponse)
def update_attendance(
    attendance_id: int,
    att: schemas.AttendanceCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db_att = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not db_att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db_att.student_id = att.student_id
    db_att.schedule_id = att.schedule_id
    db_att.status = att.status
    db_att.comment = att.comment
    if att.record_date:
        db_att.date = att.record_date
    db.commit()
    db.refresh(db_att)
    return db_att


@app.delete("/api/attendance/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    db_att = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not db_att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(db_att)
    db.commit()
    return {"status": "success", "message": "Attendance record deleted"}
