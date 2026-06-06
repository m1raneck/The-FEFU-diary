from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, CheckConstraint, Numeric
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))


class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True)


class GradeCategory(Base):
    __tablename__ = "grade_categories"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    weight = Column(Numeric(6, 4), nullable=False)


class GradeScaleRule(Base):
    __tablename__ = "grade_scale_rules"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False)
    min_points = Column(Numeric(10, 2), nullable=False)
    max_points = Column(Numeric(10, 2), nullable=False)
    final_grade = Column(Integer, nullable=False)


class GradeColumnSetting(Base):
    __tablename__ = "grade_column_settings"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False)
    grade_date = Column(Date, nullable=False)
    column_type = Column(String(10), nullable=False)


class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("grade_categories.id", ondelete="SET NULL"), nullable=True)
    grade = Column(Integer, CheckConstraint("grade BETWEEN 0 AND 100"))
    raw_score = Column(Numeric(10, 2), nullable=True)
    grade_date = Column(Date, nullable=False, server_default=func.current_date())
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
