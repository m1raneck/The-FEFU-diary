from fefu_common.config import settings
from fefu_common.database import Base, create_database

engine, SessionLocal, get_db = create_database(settings.DATABASE_URL)
