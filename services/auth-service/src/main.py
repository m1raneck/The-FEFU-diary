from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text

app = FastAPI()

# Берем URL базы из переменных окружения (которые пропишем в docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    return {"status": "Service is running!"}

@app.get("/test-db")
def test_db():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Database connection successful!"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}