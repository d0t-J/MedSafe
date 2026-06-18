from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes.health import router as health_router
from api.routes.check import router as check_router
from api.routes.auth import router as auth_router
from api.routes.history import router as history_router

from core.config import get_settings


def create_app() -> FastAPI:
    """Application factory for a service-oriented API composition."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(check_router)
    app.include_router(auth_router)
    app.include_router(history_router)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse("static/index.html")

    @app.get("/login", include_in_schema=False)
    def login():
        return FileResponse("static/login.html")

    @app.get("/profile", include_in_schema=False)
    def profile():
        return FileResponse("static/profile.html")

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app
