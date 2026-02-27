# EVA-STORY: ACA-01-003
# EVA-STORY: ACA-12-002
"""
ACA API -- FastAPI application factory.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import get_settings
from app.routers import auth, scans, findings, checkout, admin, health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown: clean up Cosmos client if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title="ACA -- Azure Cost Advisor API",
        version="0.1.0",
        docs_url="/docs" if settings.ACA_ENVIRONMENT != "production" else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ACA_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/v1/auth")
    app.include_router(scans.router, prefix="/v1/scans")
    app.include_router(findings.router, prefix="/v1/findings")
    app.include_router(checkout.router, prefix="/v1/checkout")
    app.include_router(admin.router, prefix="/v1/admin")

    return app


app = create_app()
