from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Cosmos DB
    ACA_COSMOS_URL: str = Field(..., description="Cosmos DB account URL")
    ACA_COSMOS_KEY: str = Field(..., description="Cosmos DB primary key")
    ACA_COSMOS_DB: str = Field(default="aca-db")

    # Azure OpenAI
    ACA_OPENAI_ENDPOINT: str = Field(..., description="Azure OpenAI endpoint")
    ACA_OPENAI_KEY: str = Field(..., description="Azure OpenAI key")
    ACA_OPENAI_DEPLOYMENT: str = Field(default="gpt-4o")

    # Stripe
    STRIPE_SECRET_KEY: str = Field(..., description="Stripe secret key")
    STRIPE_WEBHOOK_SECRET: str = Field(..., description="Stripe webhook signing secret")
    STRIPE_PRICE_TIER2_ONETIME: str = Field(default="")
    STRIPE_PRICE_TIER2_SUBSCRIPTION: str = Field(default="")
    STRIPE_PRICE_TIER3_ONETIME: str = Field(default="")
    STRIPE_ENABLE_SUBSCRIPTIONS: bool = Field(default=True)

    # Public URLs (used in Stripe return/cancel URLs)
    PUBLIC_APP_URL: str = Field(default="http://localhost:5173")
    PUBLIC_API_URL: str = Field(default="http://localhost:8000")

    # Cosmos container names (override per environment)
    COSMOS_CONTAINER_ENTITLEMENTS: str = Field(default="entitlements")
    COSMOS_CONTAINER_PAYMENTS: str = Field(default="payments")
    COSMOS_CONTAINER_CLIENTS: str = Field(default="clients")
    COSMOS_CONTAINER_STRIPE_CUSTOMER_MAP: str = Field(default="stripe_customer_map")
    COSMOS_CONTAINER_ADMIN_AUDIT: str = Field(default="admin_audit_events")

    # ACA API
    ACA_API_SECRET_KEY: str = Field(default="dev-secret-change-me")
    ACA_ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    ACA_ENVIRONMENT: str = Field(default="local")

    # Observability
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = Field(default="")


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
