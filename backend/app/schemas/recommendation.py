import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecommendationCreate(BaseModel):
    application_id: uuid.UUID
    recommendation_type: str
    confidence_score: float
    reasoning: str
    cost_savings_estimate: float | None = None
    alternative_app: str | None = None
    evidence: str | None = None
    created_by: str


class RecommendationUpdate(BaseModel):
    recommendation_type: str | None = None
    confidence_score: float | None = None
    reasoning: str | None = None
    cost_savings_estimate: float | None = None
    alternative_app: str | None = None
    evidence: str | None = None
    status: str | None = None
    reviewed_by: uuid.UUID | None = None
    reviewed_at: datetime | None = None


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    application_name: str | None = None
    recommendation_type: str
    confidence_score: float
    reasoning: str
    cost_savings_estimate: float | None = None
    alternative_app: str | None = None
    evidence: str | None = None
    status: str
    created_by: str
    reviewed_by: uuid.UUID | None = None
    reviewer_name: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
