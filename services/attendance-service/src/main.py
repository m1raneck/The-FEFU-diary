from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import models, schemas, database

app = FastAPI(title="Attendance Service")
security = HTTPBearer()
SECRET_KEY = "super-secret-key-for-fefu-diary"

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(database.get_db)):
    token = auth.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_teacher_role(current_user = Depends(get_current_user), db: Session = Depends(database.get_db)):
    result = db.execute(
        text("SELECT 1 FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = :uid AND r.name = 'teacher'"),
        {"uid": current_user.id}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user

@app.get("/api/attendance", response_model=list[schemas.AttendanceResponse])
def get_attendance(
    student_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    student = db.execute(
        text("SELECT id FROM students WHERE user_id = :uid"),
        {"uid": current_user.id}
    ).fetchone()
    if student:
        query = db.query(models.Attendance).filter(models.Attendance.student_id == student.id)
        if schedule_id:
            query = query.filter(models.Attendance.schedule_id == schedule_id)
        if attendance_date:
            query = query.filter(models.Attendance.date == attendance_date)
        return query.all()

    teacher = db.execute(
        text("SELECT id FROM teachers WHERE user_id = :uid"),
        {"uid": current_user.id}
    ).fetchone()
    if teacher:
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
def create_attendance(att: schemas.AttendanceCreate, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
    att_date = att.record_date or date.today()
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == att.student_id,
        models.Attendance.schedule_id == att.schedule_id,
        models.Attendance.date == att_date
    ).first()
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
        comment=att.comment
    )
    db.add(new_att)
    db.commit()
    db.refresh(new_att)
    return new_att


@app.put("/api/attendance/{attendance_id}", response_model=schemas.AttendanceResponse)
def update_attendance(attendance_id: int, att: schemas.AttendanceCreate, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
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
def delete_attendance(attendance_id: int, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
    db_att = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not db_att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(db_att)
    db.commit()
    return {"status": "success", "message": "Attendance record deleted"}
