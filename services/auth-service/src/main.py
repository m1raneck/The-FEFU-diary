from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from . import models, schemas, database

app = FastAPI(title="Auth Service")

# Настройки безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "super-secret-key-for-fefu-diary"
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/api/auth/register", response_model=schemas.StandardResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):

    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        return {"status": "error", "message": "Email already registered"}
    
    new_user = models.User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "success", "data": {"id": new_user.id}, "message": "User created"}

@app.post("/api/auth/login", response_model=schemas.StandardResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.login).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        return {"status": "error", "message": "Invalid credentials"}
    
    token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"status": "success", "data": {"token": token}, "message": None}