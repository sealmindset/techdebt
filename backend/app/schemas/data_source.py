import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Keys in auth_config that are safe to return unmasked
_NON_SENSITIVE_KEYS = {"header_name", "prefix", "token_url"}


def mask_auth_config(config: dict | None) -> dict | None:
    """Replace sensitive values with asterisks, keep structural keys visible."""
    if not config:
        return None
    return {
        k: v if k in _NON_SENSITIVE_KEYS else "••••••••"
        for k, v in config.items()
    }


class DataSourceCreate(BaseModel):
    """Create a new data source from the catalog."""
    name: str
    source_type: str
    base_url: str | None = None
    auth_method: str | None = None
    auth_config: dict | None = None
    sync_schedule: str = "manual"
    sync_enabled: bool = False
    is_primary: bool = False


class DataSourceUpdate(BaseModel):
    base_url: str | None = None
    status: str | None = None
    error_message: str | None = None


class DataSourceConfigUpdate(BaseModel):
    """Update auth configuration and sync settings."""
    auth_method: str | None = None
    auth_config: dict | None = None
    sync_schedule: str | None = None
    sync_enabled: bool | None = None


class DataSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    source_type: str
    base_url: str | None = None
    status: str
    auth_method: str | None = None
    auth_config_masked: dict | None = None
    sync_schedule: str = "manual"
    sync_enabled: bool = False
    is_primary: bool = False
    last_sync_at: datetime | None = None
    records_synced: int = 0
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    latency_ms: int | None = None


class SyncResponse(BaseModel):
    status: str
    records_synced: int | None = None
    message: str


class CatalogItem(BaseModel):
    key: str
    name: str
    vendor: str
    source_type: str
    category: str
    description: str
    default_base_url: str | None = None
    logo_letter: str


class CatalogCategory(BaseModel):
    name: str
    description: str
    items: list[CatalogItem]


# ---------------------------------------------------------------------------
# Field ownership: which source_type is authoritative for which Application
# fields.  When syncing, only the owning source_type may write these fields.
# ---------------------------------------------------------------------------
FIELD_OWNERSHIP: dict[str, list[str]] = {
    "procurement": [
        "annual_cost", "cost_per_license", "total_licenses",
        "contract_start", "contract_end", "vendor",
    ],
    "identity_analytics": [
        "active_users", "adoption_rate", "last_login_date",
    ],
    "vendor_risk": [
        "risk_score", "compliance_status",
    ],
    "spend_analytics": [
        "annual_cost", "cost_per_license",
    ],
    "cmdb": [
        "name", "vendor", "category", "app_type", "department", "description",
    ],
    "graph_discovery": [
        "active_users", "adoption_rate", "last_login_date",
        "name", "vendor", "category",
    ],
    "manual": [],  # lowest priority -- can set any field not owned by others
}
