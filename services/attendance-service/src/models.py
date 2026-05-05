from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, CheckConstraint
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

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, late
    date = Column(Date, nullable=False, server_default=func.current_date())
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())