from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from sqlalchemy.orm import joinedload
app = FastAPI(title="Schedule Service")
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
    is_teacher = any(role.name == 'teacher' for role in current_user.roles)
    
    if not is_teacher:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user

@app.get("/api/subjects", response_model=List[schemas.SubjectResponse])
def get_subjects(db: Session = Depends(database.get_db), _=Depends(get_current_user)):
    return db.query(models.Subject).all()

@app.post("/api/subjects", response_model=schemas.SubjectResponse)
def create_subject(subj: schemas.SubjectBase, db: Session = Depends(database.get_db), _=Depends(get_teacher_role)):
    existing = db.query(models.Subject).filter(models.Subject.name == subj.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject already exists")

    new_subject = models.Subject(**subj.model_dump() if hasattr(subj, "model_dump") else subj.dict())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@app.get("/api/rooms", response_model=List[schemas.RoomResponse])
def get_rooms(db: Session = Depends(database.get_db), _=Depends(get_current_user)):
    return db.query(models.Room).all()

@app.post("/api/rooms", response_model=schemas.RoomResponse)
def create_room(room: schemas.RoomBase, db: Session = Depends(database.get_db), _=Depends(get_teacher_role)):
    existing = db.query(models.Room).filter(models.Room.number == room.number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")
    
    new_room = models.Room(**room.model_dump() if hasattr(room, "model_dump") else room.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@app.get("/api/schedule")
def get_schedule(
    group_id: int = None,
    teacher_id: int = None,
    weekday: int = None,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(models.Schedule).options(
        joinedload(models.Schedule.subject),
        joinedload(models.Schedule.group),
        joinedload(models.Schedule.room)
    )
    role_names = [r.name for r in current_user.roles]

    if 'student' in role_names:
        student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if student and student.group_id:
            query = query.filter(models.Schedule.group_id == student.group_id)

    elif 'teacher' in role_names:
        teacher = db.query(models.Teacher).filter(models.Teacher.user_id == current_user.id).first()
        if teacher:
            query = query.filter(models.Schedule.teacher_id == teacher.id)

    if group_id:
        query = query.filter(models.Schedule.group_id == group_id)
    if teacher_id:
        query = query.filter(models.Schedule.teacher_id == teacher_id)
    if weekday:
        query = query.filter(models.Schedule.weekday == weekday)

    schedules = query.all()

    result = []
    for sched in schedules:
        result.append({
            "id": sched.id,
            "group_id": sched.group_id,
            "subject_id": sched.subject_id,
            "teacher_id": sched.teacher_id,
            "room_id": sched.room_id,
            "weekday": sched.weekday,
            "lesson_number": sched.lesson_number,
            "semester": sched.semester,
            "year": sched.year,
            "created_at": sched.created_at,
            "subject": {
                "id": sched.subject.id,
                "name": sched.subject.name,
                "short_name": sched.subject.short_name,
                "description": sched.subject.description
            } if sched.subject else None,
            "group": {
                "id": sched.group.id,
                "name": sched.group.name,
                "course": sched.group.course,
                "year": sched.group.year
            } if sched.group else None,
            "room": {
                "id": sched.room.id,
                "number": sched.room.number,
                "building": sched.room.building
            } if sched.room else None
        })

    return result

@app.post("/api/schedule", response_model=schemas.ScheduleResponse)
def create_schedule(sched: schemas.ScheduleBase, db: Session = Depends(database.get_db), _=Depends(get_teacher_role)):
    new_entry = models.Schedule(**sched.model_dump() if hasattr(sched, "model_dump") else sched.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry