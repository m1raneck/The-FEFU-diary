from pydantic import BaseModel, EmailStr
from typing import Optional, Any

class StandardResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    login: str
    password: str