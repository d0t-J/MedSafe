from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes.health import router as health_router
from api.routes.check import router as check_router
from api.routes.users import router as create_user
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

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(health_router)
    app.include_router(check_router)
    app.include_router(create_user)

    return app
