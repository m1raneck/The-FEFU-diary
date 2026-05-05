from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="Schedule Service")
security = HTTPBearer()
SECRET_KEY = "super-secret-key-for-fefu-diary"

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(database.get_db())):
    token = auth.credentials()
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

def get_teacher_role(current_user = Depends(get_current_user()), db: Session = Depends(database.get_db())):
    role = db.query(models.Role).filter(models.Role.name == 'teacher').first()
    if not role:
        raise HTTPException(status_code=500, detail="Role not found")
    user_role = db.query(models.user_roles).filter(
        models.user_roles.c.user_id == current_user.id,
        models.user_roles.c.role_id == role.id
    ).first()
    if not user_role:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user


@app.get("/api/subjects", response_model=list[schemas.SubjectResponse])
def get_subjects(db: Session = Depends(database.get_db()), _=Depends(get_current_user())):
    return db.query(models.Subject).all()

@app.post("/api/subjects", response_model=schemas.SubjectResponse)
def create_subject(subj: schemas.SubjectCreate, db: Session = Depends(database.get_db()), _=Depends(get_teacher_role())):
    existing = db.query(models.Subject).filter(models.Subject.name == subj.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject exists")
    new = models.Subject(**subj.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@app.get("/api/rooms", response_model=list[schemas.RoomResponse])
def get_rooms(db: Session = Depends(database.get_db()), _=Depends(get_current_user())):
    return db.query(models.Room).all()

@app.post("/api/rooms", response_model=schemas.RoomResponse)
def create_room(room: schemas.RoomCreate, db: Session = Depends(database.get_db()), _=Depends(get_teacher_role())):
    existing = db.query(models.Room).filter(models.Room.number == room.number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room exists")
    new = models.Room(**room.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@app.get("/api/schedule", response_model=list[schemas.ScheduleResponse])
def get_schedule(
    group_id: int = None,
    teacher_id: int = None,
    weekday: int = None,
    db: Session = Depends(database.get_db()),
    current_user = Depends(get_current_user())
):
    query = db.query(models.Schedule)
    # Если студент – показываем только его группу
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
    return query.all()

@app.post("/api/schedule", response_model=schemas.ScheduleResponse)
def create_schedule(sched: schemas.ScheduleCreate, db: Session = Depends(database.get_db()), _=Depends(get_teacher_role())):
    new = models.Schedule(**sched.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

