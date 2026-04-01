from pydantic import BaseModel


class SavingsOpportunity(BaseModel):
    id: str
    name: str
    vendor: str | None = None
    annual_cost: float = 0.0
    savings_estimate: float = 0.0
    recommendation_type: str | None = None


class RecentDecision(BaseModel):
    id: str
    application_name: str
    decision_type: str
    status: str
    submitted_by: str | None = None
    created_at: str | None = None


class DashboardStats(BaseModel):
    total_apps: int = 0
    total_spend: float = 0.0
    avg_adoption_rate: float = 0.0
    total_potential_savings: float = 0.0
    apps_by_status: dict[str, int] = {}
    apps_by_category: dict[str, int] = {}
    recommendations_summary: dict[str, int] = {}
    top_savings_opportunities: list[SavingsOpportunity] = []
    recent_decisions: list[RecentDecision] = []
