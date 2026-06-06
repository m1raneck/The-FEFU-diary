from fastapi import Depends, FastAPI, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from fefu_common.auth import AuthDependencies
from fefu_common.health import register_health_route
from fefu_common.tokens import create_access_token

from . import database, models, schemas

app = FastAPI(title="Auth Service")
register_health_route(app, "auth-service")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_deps = AuthDependencies(models.User, database.get_db)
get_current_user = auth_deps.current_user_dependency()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/api/auth/register", response_model=schemas.StandardResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        return {"status": "error", "message": "Email already registered"}

    if db.query(models.Student).filter(models.Student.student_number == user_data.student_number).first():
        return {"status": "error", "message": "Student number already registered"}

    try:
        new_user = models.User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
        )
        db.add(new_user)
        db.flush()

        new_student = models.Student(
            user_id=new_user.id,
            group_id=user_data.group_id if user_data.group_id != 0 else None,
            student_number=user_data.student_number,
            enrollment_year=user_data.enrollment_year,
            birth_date=user_data.birth_date,
            address=user_data.address,
        )
        db.add(new_student)

        role = db.query(models.Role).filter(models.Role.name == "student").first()
        if role:
            db.add(models.UserRole(user_id=new_user.id, role_id=role.id))

        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "data": {"id": new_user.id},
            "message": "User and Student profile created",
        }
    except IntegrityError:
        db.rollback()
        return {"status": "error", "message": "Registration conflict — duplicate data"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@app.post("/api/auth/login", response_model=schemas.StandardResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.login).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        return {"status": "error", "message": "Invalid credentials"}

    token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"status": "success", "data": {"token": token}, "message": "Login successful"}


@app.post("/api/auth/register-teacher", response_model=schemas.StandardResponse, status_code=status.HTTP_201_CREATED)
def register_teacher(teacher_data: schemas.TeacherCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == teacher_data.email).first():
        return {"status": "error", "message": "Email already registered"}

    try:
        new_user = models.User(
            email=teacher_data.email,
            password_hash=hash_password(teacher_data.password),
            full_name=teacher_data.full_name,
            phone=teacher_data.phone,
        )
        db.add(new_user)
        db.flush()

        new_teacher = models.Teacher(
            user_id=new_user.id,
            department=teacher_data.department,
            position=teacher_data.position,
            degree=teacher_data.degree,
        )
        db.add(new_teacher)

        role = db.query(models.Role).filter(models.Role.name == "teacher").first()
        if role:
            db.add(models.UserRole(user_id=new_user.id, role_id=role.id))

        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "data": {"id": new_user.id},
            "message": "Teacher profile created",
        }
    except IntegrityError:
        db.rollback()
        return {"status": "error", "message": "Registration conflict — duplicate data"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@app.get("/api/users/students")
def get_students(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    students = (
        db.query(models.User, models.Student)
        .join(models.Student, models.User.id == models.Student.user_id)
        .all()
    )
    return [
        {
            "id": student.id,
            "full_name": user.full_name,
            "student_number": student.student_number,
            "group_id": student.group_id,
        }
        for user, student in students
    ]


@app.get("/api/users/me", response_model=schemas.StandardResponse)
def read_users_me(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .options(
            joinedload(models.User.student_profile).joinedload(models.Student.group),
            joinedload(models.User.teacher_profile),
        )
        .filter(models.User.id == current_user.id)
        .first()
    )

    role_rows = db.execute(
        text("SELECT r.name FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = :uid"),
        {"uid": current_user.id},
    ).fetchall()
    roles = [row[0] for row in role_rows]

    profile_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "roles": roles,
        "student_info": None,
        "teacher_info": None,
    }

    if user.student_profile:
        sp = user.student_profile
        profile_data["student_info"] = {
            "student_id": sp.id,
            "student_number": sp.student_number,
            "group_id": sp.group_id,
            "group_name": sp.group.name if sp.group else None,
            "enrollment_year": sp.enrollment_year,
            "address": sp.address,
        }

    if user.teacher_profile:
        tp = user.teacher_profile
        profile_data["teacher_info"] = {
            "teacher_id": tp.id,
            "department": tp.department,
            "position": tp.position,
            "degree": tp.degree,
        }

    return {"status": "success", "data": profile_data, "message": None}
