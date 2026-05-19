from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional, List
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import date

from . import models, schemas, database

app = FastAPI(title="Grades Service")
security = HTTPBearer()
SECRET_KEY = "super-secret-key-for-fefu-diary"

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(database.get_db)):
    token = auth.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_teacher_role(current_user = Depends(get_current_user), db: Session = Depends(database.get_db)):
    result = db.execute(
        "SELECT 1 FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = :uid AND r.name = 'teacher'",
        {"uid": current_user.id}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user

def get_student_role(current_user = Depends(get_current_user), db: Session = Depends(database.get_db)):
    result = db.execute(
        "SELECT 1 FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = :uid AND r.name = 'student'",
        {"uid": current_user.id}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=403, detail="Student access required")
    return current_user

@app.get("/api/grades", response_model=List[schemas.GradeResponse])
def get_grades(
    student_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    student = db.execute("SELECT id FROM students WHERE user_id = :uid", {"uid": current_user.id}).fetchone()
    if student:
        query = db.query(models.Grade).filter(models.Grade.student_id == student.id)
        return query.all()
    teacher = db.execute("SELECT id FROM teachers WHERE user_id = :uid", {"uid": current_user.id}).fetchone()
    if teacher:
        query = db.query(models.Grade)
        if student_id:
            query = query.filter(models.Grade.student_id == student_id)
        return query.all()
    raise HTTPException(status_code=403, detail="No role assigned")

@app.post("/api/grades", response_model=schemas.GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(grade: schemas.GradeCreate, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
    new_grade = models.Grade(**grade.dict())
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade

@app.put("/api/grades/{grade_id}", response_model=schemas.GradeResponse)
def update_grade(grade_id: int, grade: schemas.GradeCreate, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    for key, value in grade.dict().items():
        setattr(db_grade, key, value)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@app.delete("/api/grades/{grade_id}")
def delete_grade(grade_id: int, db: Session = Depends(database.get_db), _ = Depends(get_teacher_role)):
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    db.delete(db_grade)
    db.commit()
    return {"status": "success", "message": "Grade deleted"}

# ============= BULK IMPORT ENDPOINT =============
@app.post("/api/grades/bulk")
def bulk_create_grades(
    payload: schemas.BulkGradeRequest,
    db: Session = Depends(database.get_db),
    _ = Depends(get_teacher_role)
):
    """Массовый импорт оценок из CSV"""
    created = []
    for item in payload.grades:
        existing = db.query(models.Grade).filter(
            models.Grade.student_id == item.student_id,
            models.Grade.schedule_id == payload.schedule_id,
            models.Grade.grade_date == payload.grade_date
        ).first()
        if existing:
            existing.grade = item.grade
            existing.comment = item.comment
            created.append({"student_id": item.student_id, "action": "updated"})
        else:
            new_grade = models.Grade(
                student_id=item.student_id,
                schedule_id=payload.schedule_id,
                grade=item.grade,
                grade_date=payload.grade_date,
                comment=item.comment
            )
            db.add(new_grade)
            created.append({"student_id": item.student_id, "action": "created"})
    try:
        db.commit()
        return {"status": "success", "data": created, "message": f"Processed {len(created)} grades"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))