from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


def register_health_route(
    app,
    service_name: str,
    get_db: Optional[Callable] = None,
):
    router = APIRouter(tags=["health"])

    if get_db is None:

        @router.get("/health")
        def health_check():
            return {"status": "ok", "service": service_name}

    else:

        @router.get("/health")
        def health_check(db: Session = Depends(get_db)):
            try:
                db.execute(text("SELECT 1"))
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail={"status": "degraded", "service": service_name, "database": "unavailable"},
                ) from exc
            return {"status": "ok", "service": service_name, "database": "ok"}

    app.include_router(router)
