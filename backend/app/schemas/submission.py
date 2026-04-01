import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    app_name: str
    vendor: str | None = None
    department: str
    usage_frequency: str
    business_justification: str
    user_count_estimate: int | None = None
    annual_cost_estimate: float | None = None


class SubmissionUpdate(BaseModel):
    status: str | None = None
    matched_application_id: uuid.UUID | None = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    app_name: str
    vendor: str | None = None
    department: str
    submitted_by: uuid.UUID
    submitter_name: str | None = None
    usage_frequency: str
    business_justification: str
    user_count_estimate: int | None = None
    annual_cost_estimate: float | None = None
    status: str
    matched_application_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
