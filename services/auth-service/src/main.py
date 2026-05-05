from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from . import models, schemas, database

app = FastAPI(title="Auth Service")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "super-secret-key-for-fefu-diary"
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(database.get_db())):
    token = auth.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/api/auth/register", response_model=schemas.StandardResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db())):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        return {"status": "error", "message": "Email already registered"}

    existing_student = db.query(models.Student).filter(
        models.Student.student_number == user_data.student_number
    ).first()
    if existing_student:
        return {"status": "error", "message": "Student number already registered"}

    try:
        new_user = models.User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        db.add(new_user)
        db.flush()

        new_student = models.Student(
            user_id=new_user.id,
            group_id=user_data.group_id if user_data.group_id != 0 else None,
            student_number=user_data.student_number,
            enrollment_year=user_data.enrollment_year,
            birth_date=user_data.birth_date,
            address=user_data.address
        )
        db.add(new_student)
        
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": "success", 
            "data": {"id": new_user.id}, 
            "message": "User and Student profile created"
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Database error: {str(e)}"}

@app.post("/api/auth/login", response_model=schemas.StandardResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db())):
    user = db.query(models.User).filter(models.User.email == credentials.login).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        return {"status": "error", "message": "Invalid credentials"}
    
    token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"status": "success", "data": {"token": token}, "message": "Login successful"}

@app.get("/api/users/me", response_model=schemas.StandardResponse)
def read_users_me(current_user: models.User = Depends(get_current_user())):
    profile_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "student_info": None
    }
    
    if current_user.student_profile:
        sp = current_user.student_profile
        profile_data["student_info"] = {
            "student_number": sp.student_number,
            "group_id": sp.group_id,
            "enrollment_year": sp.enrollment_year,
            "address": sp.address
        }
        
    return {
        "status": "success",
        "data": profile_data,
        "message": None
    }