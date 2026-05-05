from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    course = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    students = relationship("Student", back_populates="group")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20))

    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"))
    student_number = Column(String(50), nullable=False, unique=True, index=True)
    enrollment_year = Column(Integer, nullable=False)
    birth_date = Column(Date)
    address = Column(Text)

    user = relationship("User", back_populates="student_profile")
    group = relationship("Group", back_populates="students")

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    department = Column(String(255))
    position = Column(String(100))
    degree = Column(String(100))

    user = relationship("User", back_populates="teacher_profile")