import time
import uuid
from datetime import datetime, timezone

import httpx
import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.data_source import DataSource
from app.schemas.auth import UserInfo
from app.schemas.data_source import (
    CatalogCategory,
    CatalogItem,
    DataSourceConfigUpdate,
    DataSourceCreate,
    DataSourceOut,
    DataSourceUpdate,
    FIELD_OWNERSHIP,
    SyncResponse,
    TestConnectionResponse,
    mask_auth_config,
)

router = APIRouter(prefix="/api/data-sources", tags=["data-sources"])

# Mock service data endpoints used during sync
_SYNC_ENDPOINTS: dict[str, str] = {
    "procurement": "/api/v1/procurement/contracts",
    "vendor_risk": "/api/v1/vendors",
    "identity_analytics": "/api/v1/applications/sign-ins",
    "spend_analytics": "/api/v1/vendor-spend/summary",
    "graph_discovery": "/v1.0/intelligence/summary",
}

_HTTPX_TIMEOUT = 5.0

# ---------------------------------------------------------------------------
# Source catalog -- predefined integration types grouped by category
# ---------------------------------------------------------------------------
SOURCE_CATALOG: list[CatalogCategory] = [
    CatalogCategory(
        name="Procurement & Contracts",
        description="License costs, contract terms, and procurement data",
        items=[
            CatalogItem(key="workday", name="Workday", vendor="Workday", source_type="procurement", category="Procurement & Contracts", description="HCM and financial management including software procurement and contract data", default_base_url="https://api.workday.com", logo_letter="W"),
            CatalogItem(key="sap_ariba", name="SAP Ariba", vendor="SAP", source_type="procurement", category="Procurement & Contracts", description="Procurement and supply chain management with contract lifecycle tracking", default_base_url="https://api.ariba.com", logo_letter="S"),
            CatalogItem(key="coupa", name="Coupa", vendor="Coupa", source_type="procurement", category="Procurement & Contracts", description="Business spend management platform with procurement analytics", default_base_url="https://api.coupa.com", logo_letter="C"),
            CatalogItem(key="ivanti", name="Ivanti Neurons", vendor="Ivanti", source_type="procurement", category="Procurement & Contracts", description="IT asset management with software license tracking", default_base_url="https://api.ivanti.com", logo_letter="I"),
        ],
    ),
    CatalogCategory(
        name="Identity & Access",
        description="User activity, login data, and adoption metrics",
        items=[
            CatalogItem(key="entra_id", name="Microsoft Entra ID", vendor="Microsoft", source_type="identity_analytics", category="Identity & Access", description="Identity and access management with sign-in analytics and application usage", default_base_url="https://graph.microsoft.com", logo_letter="E"),
            CatalogItem(key="okta", name="Okta", vendor="Okta", source_type="identity_analytics", category="Identity & Access", description="Identity platform with SSO analytics and application usage reporting", default_base_url="https://your-org.okta.com/api/v1", logo_letter="O"),
            CatalogItem(key="ping_identity", name="Ping Identity", vendor="Ping Identity", source_type="identity_analytics", category="Identity & Access", description="Intelligent identity platform with access analytics", default_base_url="https://api.pingone.com", logo_letter="P"),
            CatalogItem(key="onelogin", name="OneLogin", vendor="OneLogin", source_type="identity_analytics", category="Identity & Access", description="Cloud identity and access management with usage reporting", default_base_url="https://api.onelogin.com", logo_letter="1"),
        ],
    ),
    CatalogCategory(
        name="Risk & Compliance",
        description="Vendor risk scores, compliance status, and audit findings",
        items=[
            CatalogItem(key="auditboard", name="AuditBoard", vendor="AuditBoard", source_type="vendor_risk", category="Risk & Compliance", description="Connected risk platform with vendor risk management and compliance tracking", default_base_url="https://api.auditboard.com", logo_letter="A"),
            CatalogItem(key="bitsight", name="BitSight", vendor="BitSight", source_type="vendor_risk", category="Risk & Compliance", description="Security ratings platform for continuous vendor risk monitoring", default_base_url="https://api.bitsighttech.com", logo_letter="B"),
            CatalogItem(key="security_scorecard", name="SecurityScorecard", vendor="SecurityScorecard", source_type="vendor_risk", category="Risk & Compliance", description="Security ratings and risk monitoring for vendor ecosystems", default_base_url="https://api.securityscorecard.io", logo_letter="S"),
            CatalogItem(key="prevalent", name="Prevalent", vendor="Prevalent", source_type="vendor_risk", category="Risk & Compliance", description="Third-party risk management with automated vendor assessments", default_base_url="https://api.prevalent.net", logo_letter="P"),
        ],
    ),
    CatalogCategory(
        name="Spend Analytics",
        description="Detailed SaaS spend tracking, license optimization, and renewal intelligence",
        items=[
            CatalogItem(key="zylo", name="Zylo", vendor="Zylo", source_type="spend_analytics", category="Spend Analytics", description="SaaS management platform with spend discovery and optimization", default_base_url="https://api.zylo.com", logo_letter="Z"),
            CatalogItem(key="flexera", name="Flexera One", vendor="Flexera", source_type="spend_analytics", category="Spend Analytics", description="IT asset management and SaaS spend optimization", default_base_url="https://api.flexera.com", logo_letter="F"),
            CatalogItem(key="productiv", name="Productiv", vendor="Productiv", source_type="spend_analytics", category="Spend Analytics", description="SaaS intelligence platform with engagement analytics and spend insights", default_base_url="https://api.productiv.com", logo_letter="P"),
            CatalogItem(key="torii", name="Torii", vendor="Torii", source_type="spend_analytics", category="Spend Analytics", description="SaaS management with automated discovery and license optimization", default_base_url="https://api.toriihq.com", logo_letter="T"),
        ],
    ),
    CatalogCategory(
        name="CMDB & Discovery",
        description="Application inventory discovery and configuration management",
        items=[
            CatalogItem(key="servicenow", name="ServiceNow CMDB", vendor="ServiceNow", source_type="cmdb", category="CMDB & Discovery", description="IT service management with configuration management database", default_base_url="https://your-instance.service-now.com/api", logo_letter="S"),
            CatalogItem(key="jira_sm", name="Jira Service Management", vendor="Atlassian", source_type="cmdb", category="CMDB & Discovery", description="IT service management with asset discovery and tracking", default_base_url="https://your-org.atlassian.net/rest/api/3", logo_letter="J"),
            CatalogItem(key="snow_software", name="Snow Software", vendor="Snow Software", source_type="cmdb", category="CMDB & Discovery", description="Technology intelligence with SaaS discovery and normalization", default_base_url="https://api.snowsoftware.com", logo_letter="S"),
        ],
    ),
    CatalogCategory(
        name="Platform Intelligence",
        description="Cross-platform app discovery, usage analytics, license optimization, and shadow IT detection",
        items=[
            CatalogItem(key="ms_graph", name="Microsoft Graph API", vendor="Microsoft", source_type="graph_discovery", category="Platform Intelligence", description="Unified API for Entra ID app discovery, sign-in analytics, M365 usage reports, and license utilization. Discovers shadow IT and provides real usage data for every app that authenticates through your tenant.", default_base_url="https://graph.microsoft.com", logo_letter="G"),
        ],
    ),
]


def _source_to_out(source: DataSource) -> DataSourceOut:
    """Convert DataSource model to DataSourceOut schema with masked secrets."""
    return DataSourceOut(
        id=source.id,
        name=source.name,
        source_type=source.source_type,
        base_url=source.base_url,
        status=source.status,
        auth_method=source.auth_method,
        auth_config_masked=mask_auth_config(source.auth_config),
        sync_schedule=source.sync_schedule,
        sync_enabled=source.sync_enabled,
        is_primary=source.is_primary,
        last_sync_at=source.last_sync_at,
        records_synced=source.records_synced,
        error_message=source.error_message,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


@router.get("/catalog", response_model=list[CatalogCategory])
async def get_source_catalog(
    current_user: UserInfo = Depends(require_permission("data_sources", "read")),
):
    """Return the predefined source integration catalog."""
    return SOURCE_CATALOG


@router.get("/field-ownership")
async def get_field_ownership(
    current_user: UserInfo = Depends(require_permission("data_sources", "read")),
):
    """Return the field ownership mapping (source_type -> application fields)."""
    return FIELD_OWNERSHIP


@router.post("/", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    data: DataSourceCreate,
    current_user: UserInfo = Depends(require_permission("data_sources", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new data source from the catalog."""
    # Check for duplicate name
    existing = await db.execute(
        select(DataSource).where(DataSource.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A data source named '{data.name}' already exists.",
        )

    # If marked as primary, unset any other primary of the same source_type
    if data.is_primary:
        await db.execute(
            sa.update(DataSource)
            .where(DataSource.source_type == data.source_type)
            .where(DataSource.is_primary == True)  # noqa: E712
            .values(is_primary=False)
        )

    source = DataSource(
        name=data.name,
        source_type=data.source_type,
        base_url=data.base_url,
        status="disconnected",
        auth_method=data.auth_method,
        auth_config=data.auth_config,
        sync_schedule=data.sync_schedule,
        sync_enabled=data.sync_enabled,
        is_primary=data.is_primary,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return _source_to_out(source)


@router.put("/{source_id}/primary", response_model=DataSourceOut)
async def set_primary_source(
    source_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("data_sources", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Set a data source as the primary for its source_type."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    # Unset existing primary of the same type
    await db.execute(
        sa.update(DataSource)
        .where(DataSource.source_type == source.source_type)
        .where(DataSource.is_primary == True)  # noqa: E712
        .values(is_primary=False)
    )

    source.is_primary = True
    await db.commit()
    await db.refresh(source)
    return _source_to_out(source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(
    source_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("data_sources", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a data source."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    await db.delete(source)
    await db.commit()


@router.post("/test-url", response_model=TestConnectionResponse)
async def test_url(
    data: dict,
    current_user: UserInfo = Depends(require_permission("data_sources", "create")),
):
    """Test connectivity to a URL before creating a data source."""
    base_url = data.get("base_url", "")
    if not base_url:
        return TestConnectionResponse(
            success=False, message="No URL provided."
        )

    health_url = f"{base_url}/health"
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=_HTTPX_TIMEOUT) as client:
            resp = await client.get(health_url)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if resp.status_code == 200:
            return TestConnectionResponse(
                success=True,
                message="Connection successful.",
                latency_ms=elapsed_ms,
            )
        return TestConnectionResponse(
            success=False,
            message=f"Service responded with status {resp.status_code}.",
            latency_ms=elapsed_ms,
        )
    except httpx.TimeoutException:
        return TestConnectionResponse(
            success=False, message="Connection timed out."
        )
    except httpx.ConnectError:
        return TestConnectionResponse(
            success=False, message="Could not reach the service."
        )
    except Exception as exc:
        return TestConnectionResponse(
            success=False, message=f"Connection failed: {exc}"
        )


@router.get("/", response_model=list[DataSourceOut])
async def list_data_sources(
    current_user: UserInfo = Depends(require_permission("data_sources", "read")),
    db: AsyncSession = Depends(get_db),
):
    """List all data sources with their sync status."""
    result = await db.execute(select(DataSource).order_by(DataSource.name))
    sources = result.scalars().all()
    return [_source_to_out(s) for s in sources]


@router.get("/{source_id}", response_model=DataSourceOut)
async def get_data_source(
    source_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("data_sources", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single data source with configuration details."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    return _source_to_out(source)


@router.put("/{source_id}", response_model=DataSourceOut)
async def update_data_source(
    source_id: uuid.UUID,
    data: DataSourceUpdate,
    current_user: UserInfo = Depends(require_permission("data_sources", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update a data source's basic fields."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return _source_to_out(source)


@router.put("/{source_id}/config", response_model=DataSourceOut)
async def update_data_source_config(
    source_id: uuid.UUID,
    data: DataSourceConfigUpdate,
    current_user: UserInfo = Depends(require_permission("data_sources", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update a data source's auth and sync configuration."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    if source.source_type == "manual":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voluntary submissions cannot be configured via API",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return _source_to_out(source)


@router.post(
    "/{source_id}/test-connection",
    response_model=TestConnectionResponse,
)
async def test_connection(
    source_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("data_sources", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Test connectivity to the data source's endpoint."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    if source.source_type == "manual":
        return TestConnectionResponse(
            success=False,
            message="Voluntary submissions do not support connection testing.",
        )

    if not source.base_url:
        return TestConnectionResponse(
            success=False,
            message="No base URL configured for this data source.",
        )

    health_url = f"{source.base_url}/health"
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=_HTTPX_TIMEOUT) as client:
            resp = await client.get(health_url)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if resp.status_code == 200:
            return TestConnectionResponse(
                success=True,
                message=f"Connected to {source.name} successfully.",
                latency_ms=elapsed_ms,
            )
        return TestConnectionResponse(
            success=False,
            message=f"Service responded with status {resp.status_code}.",
            latency_ms=elapsed_ms,
        )
    except httpx.TimeoutException:
        return TestConnectionResponse(
            success=False,
            message="Connection timed out after 5 seconds.",
        )
    except httpx.ConnectError:
        return TestConnectionResponse(
            success=False,
            message="Could not reach the service. Check the base URL and network connectivity.",
        )
    except Exception as exc:
        return TestConnectionResponse(
            success=False,
            message=f"Connection failed: {exc}",
        )


@router.post("/{source_id}/sync", response_model=SyncResponse)
async def trigger_sync(
    source_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("data_sources", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Trigger an immediate data sync from the source."""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    if source.source_type == "manual":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voluntary submissions cannot be synced via API.",
        )

    if not source.base_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No base URL configured. Complete setup first.",
        )

    # Mark as syncing
    source.status = "syncing"
    source.error_message = None
    await db.commit()

    # Hit the mock service data endpoint
    data_path = _SYNC_ENDPOINTS.get(source.source_type, "/health")
    data_url = f"{source.base_url}{data_path}"

    try:
        async with httpx.AsyncClient(timeout=_HTTPX_TIMEOUT) as client:
            resp = await client.get(data_url)

        if resp.status_code == 200:
            body = resp.json()
            # Count records: look for list at top level or nested under common keys
            if isinstance(body, list):
                count = len(body)
            elif isinstance(body, dict):
                for key in ("data", "contracts", "vendors", "applications", "items"):
                    if key in body and isinstance(body[key], list):
                        count = len(body[key])
                        break
                else:
                    count = source.records_synced  # keep existing count
            else:
                count = source.records_synced

            source.status = "connected"
            source.records_synced = count
            source.last_sync_at = datetime.now(timezone.utc)
            source.error_message = None
            await db.commit()
            await db.refresh(source)

            return SyncResponse(
                status="completed",
                records_synced=count,
                message=f"Synced {count} records from {source.name}.",
            )
        else:
            source.status = "error"
            source.error_message = f"Sync failed: service returned {resp.status_code}"
            await db.commit()
            return SyncResponse(
                status="error",
                message=f"Service returned status {resp.status_code}.",
            )
    except Exception as exc:
        source.status = "error"
        source.error_message = f"Sync failed: {exc}"
        await db.commit()
        return SyncResponse(
            status="error",
            message=f"Sync failed: {exc}",
        )
