from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Entra / JWT
    ENTRA_TENANT_ID: str = Field(default="", description="Primary tenant id")
    ENTRA_AUDIENCE: str = Field(..., description="Expected app audience / api://... or client id")
    ENTRA_ALLOWED_ISSUERS: List[str] = Field(default_factory=list, description="Allowed token issuers")
    ENTRA_GROUPS_CLAIM_MODE: str = Field(default="groups", description="'groups' or 'roles' or 'both'")

    # Optional explicit mappings from Entra group ids to ACA roles
    ENTRA_ADMIN_GROUP_IDS: List[str] = Field(default_factory=list)
    ENTRA_SUPPORT_GROUP_IDS: List[str] = Field(default_factory=list)
    ENTRA_FINOPS_GROUP_IDS: List[str] = Field(default_factory=list)

    # Cosmos
    COSMOS_ENDPOINT: str = Field(...)
    COSMOS_KEY: str = Field(...)
    COSMOS_DB_NAME: str = Field(default="aca")

    COSMOS_CONTAINER_ENTITLEMENTS: str = "entitlements"
    COSMOS_CONTAINER_CLIENTS: str = "clients"
    COSMOS_CONTAINER_PAYMENTS: str = "payments"
    COSMOS_CONTAINER_STRIPE_CUSTOMER_MAP: str = "stripe_customer_map"
    COSMOS_CONTAINER_SCANS: str = "scans"
    COSMOS_CONTAINER_FINDINGS: str = "findings"
    COSMOS_CONTAINER_ADMIN_AUDIT: str = "admin_audit"
    COSMOS_CONTAINER_ANALYSES: str = "analyses"
    COSMOS_CONTAINER_DELIVERABLES: str = "deliverables"

settings = Settings()
