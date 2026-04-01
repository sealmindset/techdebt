import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DecisionCreate(BaseModel):
    application_id: uuid.UUID
    recommendation_id: uuid.UUID | None = None
    decision_type: str
    justification: str
    target_date: datetime | None = None
    cost_impact: float | None = None


class DecisionUpdate(BaseModel):
    decision_type: str | None = None
    justification: str | None = None
    status: str | None = None
    review_notes: str | None = None
    target_date: datetime | None = None
    cost_impact: float | None = None


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    application_name: str | None = None
    recommendation_id: uuid.UUID | None = None
    decision_type: str
    justification: str
    submitted_by: uuid.UUID
    submitter_name: str | None = None
    status: str
    reviewer_id: uuid.UUID | None = None
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    target_date: datetime | None = None
    cost_impact: float | None = None
    created_at: datetime
    updated_at: datetime
