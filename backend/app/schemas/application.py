import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    name: str
    vendor: str
    category: str
    description: str | None = None
    app_type: str
    status: str = "active"
    annual_cost: float | None = None
    cost_per_license: float | None = None
    total_licenses: int | None = None
    active_users: int | None = None
    adoption_rate: float | None = None
    last_login_date: datetime | None = None
    contract_start: datetime | None = None
    contract_end: datetime | None = None
    department: str | None = None
    data_source: str = "manual"
    risk_score: float | None = None
    compliance_status: str | None = None
    owner_id: uuid.UUID | None = None


class ApplicationUpdate(BaseModel):
    name: str | None = None
    vendor: str | None = None
    category: str | None = None
    description: str | None = None
    app_type: str | None = None
    status: str | None = None
    annual_cost: float | None = None
    cost_per_license: float | None = None
    total_licenses: int | None = None
    active_users: int | None = None
    adoption_rate: float | None = None
    last_login_date: datetime | None = None
    contract_start: datetime | None = None
    contract_end: datetime | None = None
    department: str | None = None
    data_source: str | None = None
    risk_score: float | None = None
    compliance_status: str | None = None
    owner_id: uuid.UUID | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    vendor: str
    category: str
    description: str | None = None
    app_type: str
    status: str
    annual_cost: float | None = None
    cost_per_license: float | None = None
    total_licenses: int | None = None
    active_users: int | None = None
    adoption_rate: float | None = None
    last_login_date: datetime | None = None
    contract_start: datetime | None = None
    contract_end: datetime | None = None
    department: str | None = None
    data_source: str
    risk_score: float | None = None
    compliance_status: str | None = None
    owner_id: uuid.UUID | None = None
    owner_name: str | None = None
    potential_savings: float | None = None
    created_at: datetime
    updated_at: datetime
