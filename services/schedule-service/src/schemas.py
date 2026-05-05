from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime, date

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


class SubjectBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: int
    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    number: str
    building: Optional[str] = None


class RoomResponse(RoomBase):
    id: int
    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    room_id: Optional[int] = None
    weekday: int   # 1-7
    lesson_number: int  # 1-8
    semester: int
    year: int


class ScheduleResponse(ScheduleBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class GradeBase(BaseModel):
    student_id: int
    schedule_id: int
    grade: Optional[int] = None
    comment: Optional[str] = None

class GradeCreate(GradeBase):
    grade_date: Optional[date] = None

class GradeResponse(GradeBase):
    id: int
    grade_date: date
    created_at: datetime
    class Config:
        orm_mode = True

class AttendanceBase(BaseModel):
    student_id: int
    schedule_id: int
    status: str
    comment: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    date: date
    created_at: datetime
    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str
    course: int
    year: int


class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True