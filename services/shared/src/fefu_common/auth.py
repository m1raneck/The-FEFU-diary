from typing import Callable, Type

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings

security = HTTPBearer()


class AuthDependencies:

    def __init__(self, user_model: Type, get_db: Callable):
        self.user_model = user_model
        self.get_db = get_db

    def current_user_dependency(self):
        user_model = self.user_model
        get_db = self.get_db

        def get_current_user(
            auth: HTTPAuthorizationCredentials = Depends(security),
            db: Session = Depends(get_db),
        ):
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            try:
                payload = jwt.decode(
                    token=auth.credentials,
                    key=settings.SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM],
                )
            except JWTError:
                raise credentials_exception

            user_id = payload.get("user_id")
            if user_id is not None:
                user = db.query(user_model).filter(user_model.id == user_id).first()
                if user:
                    return user

            email = payload.get("sub")
            if email:
                user = db.query(user_model).filter(user_model.email == email).first()
                if user:
                    return user

            raise credentials_exception

        return get_current_user

    def teacher_role_dependency(self, get_current_user):
        get_db = self.get_db

        def require_teacher(
            current_user=Depends(get_current_user),
            db: Session = Depends(get_db),
        ):
            result = db.execute(
                text(
                    "SELECT 1 FROM user_roles ur "
                    "JOIN roles r ON ur.role_id = r.id "
                    "WHERE ur.user_id = :uid AND r.name = 'teacher'"
                ),
                {"uid": current_user.id},
            ).fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Teacher access required",
                )
            return current_user

        return require_teacher

    def user_has_role(self, db: Session, user_id: int, role_name: str) -> bool:
        result = db.execute(
            text(
                "SELECT 1 FROM user_roles ur "
                "JOIN roles r ON ur.role_id = r.id "
                "WHERE ur.user_id = :uid AND r.name = :role"
            ),
            {"uid": user_id, "role": role_name},
        ).fetchone()
        return result is not None

    def get_profile_ids(self, db: Session, user_id: int) -> dict:
        student = db.execute(
            text("SELECT id FROM students WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchone()
        teacher = db.execute(
            text("SELECT id FROM teachers WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchone()
        return {
            "student_id": student[0] if student else None,
            "teacher_id": teacher[0] if teacher else None,
        }
