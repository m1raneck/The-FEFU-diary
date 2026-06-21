FROM python:3.11-slim
WORKDIR /app
COPY services/auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/shared/src/fefu_common ./fefu_common
COPY services/auth-service/src ./src
ENV PYTHONPATH=/app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
