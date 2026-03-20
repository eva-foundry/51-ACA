# EVA-STORY: ACA-01-003
# EVA-STORY: ACA-12-002
"""
ACA API -- FastAPI application factory.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import get_settings
from app.middleware.timing import TimingMiddleware
from app.routers import auth, scans, findings, checkout, admin, health, collect, reports, billing, webhooks, entitlements, onboarding, preflight

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
    app.add_middleware(TimingMiddleware)

    # Pre-flight health checks (runs early to warn clients)
    app.include_router(preflight.router)
    app.include_router(health.router)
    app.include_router(auth.router, prefix="/v1/auth")
    app.include_router(collect.router, prefix="/v1/collect")
    app.include_router(reports.router, prefix="/v1/reports")
    app.include_router(billing.router, prefix="/v1/billing")
    app.include_router(webhooks.router, prefix="/v1/webhooks")
    app.include_router(entitlements.router, prefix="/v1/entitlements")
    app.include_router(onboarding.router, prefix="/v1/onboarding")
    app.include_router(scans.router, prefix="/v1/scans")
    app.include_router(findings.router, prefix="/v1/findings")
    app.include_router(checkout.router, prefix="/v1/checkout")
    app.include_router(admin.router, prefix="/v1/admin")

    return app


app = create_app()
