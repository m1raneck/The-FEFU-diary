from typing import List, Optional

from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from fefu_common.auth import AuthDependencies
from fefu_common.health import register_health_route

from . import database, models, schemas

app = FastAPI(title="Schedule Service")
register_health_route(app, "schedule-service", database.get_db)

auth_deps = AuthDependencies(models.User, database.get_db)
get_current_user = auth_deps.current_user_dependency()
get_teacher_role = auth_deps.teacher_role_dependency(get_current_user)


@app.get("/api/subjects", response_model=List[schemas.SubjectResponse])
def get_subjects(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Subject).all()


@app.post("/api/subjects", response_model=schemas.SubjectResponse)
def create_subject(
    subj: schemas.SubjectBase,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    if db.query(models.Subject).filter(models.Subject.name == subj.name).first():
        raise HTTPException(status_code=400, detail="Subject already exists")

    new_subject = models.Subject(**subj.model_dump())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@app.get("/api/rooms", response_model=List[schemas.RoomResponse])
def get_rooms(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Room).all()


@app.post("/api/rooms", response_model=schemas.RoomResponse)
def create_room(
    room: schemas.RoomBase,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    if db.query(models.Room).filter(models.Room.number == room.number).first():
        raise HTTPException(status_code=400, detail="Room already exists")

    new_room = models.Room(**room.model_dump())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@app.get("/api/schedule")
def get_schedule(
    group_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    weekday: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Schedule).options(
        joinedload(models.Schedule.subject),
        joinedload(models.Schedule.group),
        joinedload(models.Schedule.room),
    )

    if auth_deps.user_has_role(db, current_user.id, "student"):
        student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if student and student.group_id:
            query = query.filter(models.Schedule.group_id == student.group_id)
    elif auth_deps.user_has_role(db, current_user.id, "teacher"):
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

    return [
        {
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
                "description": sched.subject.description,
            }
            if sched.subject
            else None,
            "group": {
                "id": sched.group.id,
                "name": sched.group.name,
                "course": sched.group.course,
                "year": sched.group.year,
            }
            if sched.group
            else None,
            "room": {
                "id": sched.room.id,
                "number": sched.room.number,
                "building": sched.room.building,
            }
            if sched.room
            else None,
        }
        for sched in schedules
    ]


@app.post("/api/schedule", response_model=schemas.ScheduleResponse)
def create_schedule(
    sched: schemas.ScheduleBase,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    new_entry = models.Schedule(**sched.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@app.get("/api/lesson-comments", response_model=List[schemas.LessonCommentResponse])
def get_lesson_comments(
    schedule_id: Optional[int] = None,
    student_id: Optional[int] = None,
    lesson_date: Optional[date] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    profiles = auth_deps.get_profile_ids(db, current_user.id)

    if profiles["student_id"]:
        query = db.query(models.LessonComment).filter(
            models.LessonComment.student_id == profiles["student_id"]
        )
        if schedule_id:
            query = query.filter(models.LessonComment.schedule_id == schedule_id)
        if lesson_date:
            query = query.filter(models.LessonComment.lesson_date == lesson_date)
        return query.order_by(models.LessonComment.lesson_date).all()

    if profiles["teacher_id"]:
        query = db.query(models.LessonComment)
        if student_id:
            query = query.filter(models.LessonComment.student_id == student_id)
        if schedule_id:
            query = query.filter(models.LessonComment.schedule_id == schedule_id)
        if lesson_date:
            query = query.filter(models.LessonComment.lesson_date == lesson_date)
        return query.order_by(models.LessonComment.lesson_date).all()

    raise HTTPException(status_code=403, detail="No role assigned")


@app.post("/api/lesson-comments")
def upsert_lesson_comment(
    payload: schemas.LessonCommentCreate,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(get_teacher_role),
):
    lesson_date = payload.lesson_date or date.today()
    comment_text = (payload.comment or "").strip()

    existing = (
        db.query(models.LessonComment)
        .filter(
            models.LessonComment.student_id == payload.student_id,
            models.LessonComment.schedule_id == payload.schedule_id,
            models.LessonComment.lesson_date == lesson_date,
        )
        .first()
    )

    if not comment_text:
        if existing:
            db.delete(existing)
            db.commit()
        return JSONResponse(status_code=200, content={"status": "deleted"})

    if existing:
        existing.comment = comment_text
        db.commit()
        db.refresh(existing)
        return existing

    row = models.LessonComment(
        student_id=payload.student_id,
        schedule_id=payload.schedule_id,
        lesson_date=lesson_date,
        comment=comment_text,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
