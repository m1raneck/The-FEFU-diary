from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def create_database(database_url: str):
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    return engine, session_factory, get_db
