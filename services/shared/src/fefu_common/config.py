import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@postgres:5432/university_db",
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-fefu-diary")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
