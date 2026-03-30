from fastapi import FastAPI
from app.api.v1.routes.user import router as user_router
from app.api.v1.routes.health import router as health_router

def create_app() -> FastAPI:
    app = FastAPI(title="Challenge Python CRUD", version="1.0.0")

    @app.get("/")
    def health_check():
        return { "status": "ok" }
    
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")

    return app

app = create_app()