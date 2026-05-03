from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import date

class StandardResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    
    group_id: Optional[int] = None
    student_number: str
    enrollment_year: int
    birth_date: Optional[date] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    login: str
    password: str