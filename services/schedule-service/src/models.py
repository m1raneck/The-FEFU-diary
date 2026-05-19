from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# таблица для связи многие-ко-многим между пользователями и ролями
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String, nullable=True)
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # 'student', 'teacher', 'admin'
    
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    short_name = Column(String, nullable=True)
    description = Column(String, nullable=True)

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    building = Column(String, nullable=True)

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    course = Column(Integer)
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    student_number = Column(String, unique=True)
    enrollment_year = Column(Integer)

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String, nullable=True)

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    
    weekday = Column(Integer) 
    lesson_number = Column(Integer)
    semester = Column(Integer)
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject")
    group = relationship("Group")
    teacher = relationship("Teacher")
    room = relationship("Room")