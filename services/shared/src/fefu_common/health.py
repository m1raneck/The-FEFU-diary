from fastapi import APIRouter


def register_health_route(app, service_name: str):
    router = APIRouter(tags=["health"])

    @router.get("/health")
    def health_check():
        return {"status": "ok", "service": service_name}

    app.include_router(router)
