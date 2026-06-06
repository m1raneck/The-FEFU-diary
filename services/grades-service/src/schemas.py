from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List
from datetime import datetime, date
from decimal import Decimal


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
        from_attributes = True


class RoomBase(BaseModel):
    number: str
    building: Optional[str] = None


class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True


class ScheduleBase(BaseModel):
    group_id: int
    subject_id: int
    teacher_id: int
    room_id: Optional[int] = None
    weekday: int
    lesson_number: int
    semester: int
    year: int


class ScheduleResponse(ScheduleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GradeCategoryBase(BaseModel):
    code: str = Field(..., max_length=20, examples=["DZ", "KR"])
    name: str = Field(..., max_length=100, examples=["Домашняя работа"])
    weight: float = Field(..., gt=0, examples=[0.3])
    max_points: float = Field(100, gt=0, examples=[10])


class GradeCategorySetRequest(BaseModel):
    schedule_id: int
    categories: List[GradeCategoryBase]


class GradeCategoryCreate(GradeCategoryBase):
    schedule_id: int


class GradeCategoryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    weight: Optional[float] = Field(None, gt=0)
    max_points: Optional[float] = Field(None, gt=0)


class GradeCategoryResponse(GradeCategoryBase):
    id: int
    schedule_id: int

    class Config:
        from_attributes = True


class GradeScaleRuleBase(BaseModel):
    min_points: float = Field(..., examples=[5])
    max_points: float = Field(..., examples=[10])
    final_grade: int = Field(..., ge=2, le=5, examples=[3])


class GradeScaleSetRequest(BaseModel):
    schedule_id: int
    rules: List[GradeScaleRuleBase]


class GradeScaleRuleResponse(GradeScaleRuleBase):
    id: int
    schedule_id: int

    class Config:
        from_attributes = True


class ConvertScoreRequest(BaseModel):
    schedule_id: int
    raw_score: float


class ConvertScoreResponse(BaseModel):
    raw_score: float
    final_grade: Optional[int]
    matched: bool


class WeightedScoreItem(BaseModel):
    category_id: int
    raw_score: float


class CalculateFinalRequest(BaseModel):
    schedule_id: int
    entries: List[WeightedScoreItem]


class CalculateFinalResponse(BaseModel):
    weighted_percent: Optional[float]
    final_grade: Optional[int]
    matched_by_scale: bool


class GradeBase(BaseModel):
    student_id: int
    schedule_id: int
    grade: Optional[int] = None
    raw_score: Optional[float] = None
    category_id: Optional[int] = None
    comment: Optional[str] = None


class GradeCreate(GradeBase):
    grade_date: Optional[date] = None
    auto_convert: bool = False


class GradeResponse(GradeBase):
    id: int
    grade_date: date
    created_at: datetime

    class Config:
        from_attributes = True


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
        from_attributes = True


class GroupBase(BaseModel):
    name: str
    course: int
    year: int


class GroupResponse(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BulkGradeItem(BaseModel):
    student_id: int
    grade: Optional[int] = None
    raw_score: Optional[float] = None
    category_id: Optional[int] = None
    comment: Optional[str] = None
    auto_convert: bool = False


class BulkGradeRequest(BaseModel):
    schedule_id: int
    grade_date: date
    grades: List[BulkGradeItem]
