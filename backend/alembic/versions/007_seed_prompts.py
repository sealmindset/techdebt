"""Seed AI prompt management -- rationalization prompts, versions, usages, tags, test cases

Revision ID: 007
Revises: 006
Create Date: 2025-01-01 00:00:00.000000

Seeds the full AI prompt library for TechDebt's rationalization engine:
- 8 managed prompts covering the complete recommendation pipeline
- Initial versions with production-ready prompt content
- Usage locations mapping prompts to features
- Tags for discoverability
- Test cases for regression testing
"""
from typing import Sequence, Union

import uuid
import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Deterministic UUID namespace (same as 005)
# ---------------------------------------------------------------------------
NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _uuid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# Prompt definitions
# ---------------------------------------------------------------------------

PROMPTS = [
    {
        "id": _uuid("prompt-app-rationalization"),
        "slug": "app-rationalization",
        "name": "Application Rationalization",
        "description": "Primary prompt that analyzes an application's usage, cost, adoption, and risk data to produce a keep/cut/replace/consolidate recommendation with confidence score and evidence.",
        "category": "rationalization",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are an enterprise IT rationalization analyst. Your job is to evaluate software applications based on quantitative data (cost, usage, adoption, licensing) and qualitative signals (business criticality, vendor risk, integration complexity) to recommend whether to keep, cut, replace, or consolidate each application.\n\nYou must be objective and data-driven. Every recommendation must cite specific evidence from the provided data. Confidence scores must reflect the quality and completeness of the input data.",
        "content": """Analyze the following application and recommend one of: KEEP, CUT, REPLACE, or CONSOLIDATE.

## Application Data
- **Name:** {{app_name}}
- **Vendor:** {{vendor}}
- **Category:** {{category}}
- **Annual Cost:** ${{annual_cost}}
- **Cost per License:** ${{cost_per_license}}
- **Total Licenses:** {{total_licenses}}
- **Active Users (last 90 days):** {{active_users}}
- **Adoption Rate:** {{adoption_rate}}%
- **Business Criticality:** {{business_criticality}}
- **Integration Count:** {{integration_count}}
- **Contract Renewal Date:** {{renewal_date}}
- **Vendor Risk Score:** {{vendor_risk_score}}/100

## Analysis Requirements
1. Calculate license utilization (active_users / total_licenses)
2. Calculate cost per active user (annual_cost / active_users)
3. Assess adoption trend (is adoption improving, stable, or declining?)
4. Evaluate vendor risk and contract timing
5. Consider integration dependencies

## Output Format
Respond with a JSON object:
```json
{
  "recommendation": "KEEP | CUT | REPLACE | CONSOLIDATE",
  "confidence": 0.0-1.0,
  "reasoning": "2-3 sentence summary",
  "evidence": [
    "Specific data point supporting the recommendation",
    "Another supporting data point"
  ],
  "cost_savings_estimate": 0.00,
  "risk_factors": ["factor1", "factor2"],
  "alternative_app": "name or null"
}
```""",
        "parameters": {
            "temperature": 0.2,
            "max_tokens": 1024,
            "top_p": 0.95
        },
        "tags": ["core", "rationalization", "recommendations"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Called when generating recommendations for individual applications", "is_primary": True},
            {"usage_type": "api", "location": "/api/recommendations", "description": "Triggered via POST /api/recommendations when creating AI-generated recommendations", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Low adoption app should recommend CUT",
                "input_data": {"app_name": "Legacy CRM", "vendor": "OldVendor", "category": "Sales", "annual_cost": 120000, "cost_per_license": 100, "total_licenses": 500, "active_users": 45, "adoption_rate": 9.0, "business_criticality": "low", "integration_count": 1, "renewal_date": "2026-06-01", "vendor_risk_score": 72},
                "expected_output": "CUT",
                "notes": "9% adoption with low criticality and high vendor risk should strongly favor CUT"
            },
            {
                "name": "High adoption critical app should recommend KEEP",
                "input_data": {"app_name": "Slack", "vendor": "Salesforce", "category": "Communication", "annual_cost": 180000, "cost_per_license": 15, "total_licenses": 12000, "active_users": 11500, "adoption_rate": 95.8, "business_criticality": "critical", "integration_count": 24, "renewal_date": "2027-01-15", "vendor_risk_score": 12},
                "expected_output": "KEEP",
                "notes": "95.8% adoption, critical business function, low vendor risk = strong KEEP"
            },
        ],
    },
    {
        "id": _uuid("prompt-cost-savings-analysis"),
        "slug": "cost-savings-analysis",
        "name": "Cost Savings Analysis",
        "description": "Calculates detailed cost savings from license optimization, vendor consolidation, and contract renegotiation opportunities for an application or group of applications.",
        "category": "rationalization",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are a financial analyst specializing in enterprise software spend optimization. You calculate precise savings estimates with clear methodology and conservative assumptions. Always show your math.",
        "content": """Calculate potential cost savings for the following application(s).

## Application Portfolio
{{#each applications}}
### {{name}} ({{vendor}})
- Annual Cost: ${{annual_cost}}
- Total Licenses: {{total_licenses}}
- Active Users: {{active_users}}
- Cost per License: ${{cost_per_license}}
- Contract End: {{renewal_date}}
- Current Recommendation: {{recommendation_type}}
{{/each}}

## Analysis Required
1. **License Reclamation:** Calculate savings from removing unused licenses (total - active * cost_per_license)
2. **Consolidation Savings:** If apps overlap in function, estimate savings from retiring duplicates
3. **Renegotiation Opportunity:** If utilization < 70%, estimate savings from right-sizing the contract
4. **Timeline:** Account for contract end dates -- savings can only be realized at renewal

## Output Format
```json
{
  "total_annual_savings": 0.00,
  "savings_breakdown": {
    "license_reclamation": 0.00,
    "consolidation": 0.00,
    "renegotiation": 0.00
  },
  "timeline": "immediate | next_renewal | phased",
  "methodology": "Brief explanation of how savings were calculated",
  "risks": ["Implementation risk", "User impact risk"]
}
```""",
        "parameters": {
            "temperature": 0.1,
            "max_tokens": 1500,
            "top_p": 0.9
        },
        "tags": ["core", "finance", "savings"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Called to generate savings estimates for dashboard and recommendations", "is_primary": True},
            {"usage_type": "page", "location": "/dashboard", "description": "Powers the savings opportunities section on the dashboard", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Unused licenses produce reclamation savings",
                "input_data": {"applications": [{"name": "Zoom", "vendor": "Zoom", "annual_cost": 96000, "total_licenses": 800, "active_users": 400, "cost_per_license": 120, "renewal_date": "2026-09-01", "recommendation_type": "keep"}]},
                "expected_output": "license_reclamation: $48,000",
                "notes": "400 unused licenses * $120 = $48,000 reclamation opportunity"
            },
        ],
    },
    {
        "id": _uuid("prompt-consolidation-finder"),
        "slug": "consolidation-finder",
        "name": "Consolidation Opportunity Finder",
        "description": "Identifies groups of overlapping applications within the same category that can be consolidated into a single platform, ranking opportunities by savings and feasibility.",
        "category": "rationalization",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are an enterprise architect specializing in application portfolio optimization. You identify functional overlaps between applications and recommend consolidation paths that minimize disruption while maximizing savings.",
        "content": """Identify consolidation opportunities in the following application category.

## Category: {{category}}
{{#each applications}}
### {{name}} ({{vendor}})
- Annual Cost: ${{annual_cost}}
- Active Users: {{active_users}}
- Adoption Rate: {{adoption_rate}}%
- Key Functions: {{key_functions}}
- Integrations: {{integrations}}
{{/each}}

## Analysis Requirements
1. Group overlapping applications by primary function
2. For each overlap group, recommend a consolidation target (the app to keep)
3. Score each opportunity: savings potential, migration complexity, user impact
4. Consider integration dependencies -- high-integration apps are harder to retire

## Output Format
```json
{
  "consolidation_groups": [
    {
      "function": "Primary business function",
      "keep": "App to retain",
      "retire": ["App1 to retire", "App2 to retire"],
      "annual_savings": 0.00,
      "migration_complexity": "low | medium | high",
      "user_impact": "minimal | moderate | significant",
      "rationale": "Why this consolidation makes sense"
    }
  ],
  "total_savings": 0.00,
  "implementation_order": ["group1", "group2"]
}
```""",
        "parameters": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "top_p": 0.9
        },
        "tags": ["core", "rationalization", "consolidation"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Runs periodic consolidation analysis across application categories", "is_primary": True},
        ],
        "test_cases": [
            {
                "name": "Two overlapping project management tools",
                "input_data": {"category": "Project Management", "applications": [{"name": "Jira", "vendor": "Atlassian", "annual_cost": 180000, "active_users": 850, "adoption_rate": 85.0, "key_functions": "issue tracking, sprint planning, roadmaps", "integrations": "GitHub, Slack, Confluence"}, {"name": "Monday.com", "vendor": "Monday", "annual_cost": 72000, "active_users": 120, "adoption_rate": 24.0, "key_functions": "task tracking, project boards, timelines", "integrations": "Slack"}]},
                "expected_output": "CONSOLIDATE: Keep Jira, retire Monday.com",
                "notes": "Jira has much higher adoption and more integrations -- Monday.com is the clear retirement candidate"
            },
        ],
    },
    {
        "id": _uuid("prompt-vendor-risk-assessment"),
        "slug": "vendor-risk-assessment",
        "name": "Vendor Risk Assessment",
        "description": "Evaluates vendor health, security posture, and business continuity risk using data from AuditBoard and public signals to produce a risk score and mitigation recommendations.",
        "category": "risk",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are a third-party risk management analyst. You evaluate vendor risk based on security assessments, financial health indicators, and compliance certifications. Be thorough but practical -- focus on risks that could materially impact the organization.",
        "content": """Assess vendor risk for the following application vendor.

## Vendor Information
- **Vendor:** {{vendor_name}}
- **Application:** {{app_name}}
- **Annual Spend:** ${{annual_spend}}
- **Contract Type:** {{contract_type}}
- **Data Classification:** {{data_classification}}

## AuditBoard Assessment Data
- **Overall Risk Score:** {{audit_risk_score}}/100
- **SOC 2 Status:** {{soc2_status}}
- **Last Assessment Date:** {{last_assessment_date}}
- **Open Findings:** {{open_findings}}
- **Critical Findings:** {{critical_findings}}

## Analysis Requirements
1. Evaluate security posture (SOC 2, open findings, data handling)
2. Assess business continuity risk (vendor size, market position, financial stability)
3. Review compliance alignment (data classification vs controls)
4. Consider concentration risk (how dependent are we on this vendor?)
5. Score overall risk 1-100 (higher = more risk)

## Output Format
```json
{
  "risk_score": 0-100,
  "risk_level": "low | medium | high | critical",
  "risk_factors": [
    {"factor": "description", "severity": "low|medium|high", "mitigation": "recommended action"}
  ],
  "compliance_gaps": ["gap1", "gap2"],
  "recommendations": ["action1", "action2"],
  "next_review_date": "YYYY-MM-DD"
}
```""",
        "parameters": {
            "temperature": 0.15,
            "max_tokens": 1200,
            "top_p": 0.9
        },
        "tags": ["risk", "vendor", "compliance", "auditboard"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Processes AuditBoard vendor assessment data into risk scores", "is_primary": True},
            {"usage_type": "page", "location": "/applications/[id]", "description": "Shows vendor risk assessment on the app detail page", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Vendor with critical findings should score high risk",
                "input_data": {"vendor_name": "SketchyCloud", "app_name": "SketchyApp", "annual_spend": 50000, "contract_type": "SaaS", "data_classification": "confidential", "audit_risk_score": 78, "soc2_status": "expired", "last_assessment_date": "2024-06-15", "open_findings": 12, "critical_findings": 3},
                "expected_output": "risk_level: critical",
                "notes": "Expired SOC 2 + 3 critical findings + confidential data = critical risk"
            },
        ],
    },
    {
        "id": _uuid("prompt-usage-trend-analysis"),
        "slug": "usage-trend-analysis",
        "name": "Usage Trend Analysis",
        "description": "Analyzes Entra ID sign-in data over time to identify adoption trends (growing, stable, declining) and predict future usage patterns for each application.",
        "category": "analytics",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are a data analyst specializing in enterprise software adoption patterns. You analyze sign-in telemetry to identify trends and predict future usage. Be precise with numbers and flag any data quality concerns.",
        "content": """Analyze usage trends for the following application based on sign-in data.

## Application
- **Name:** {{app_name}}
- **Category:** {{category}}
- **Total Licensed Users:** {{total_licenses}}

## Sign-in Data (from Entra ID)
{{#each monthly_data}}
- **{{month}}:** {{unique_users}} unique users, {{total_signins}} sign-ins, {{avg_session_minutes}} avg session (min)
{{/each}}

## Analysis Requirements
1. Calculate month-over-month growth rate for unique users
2. Identify the trend: growing (>5% MoM), stable (-5% to +5%), or declining (<-5%)
3. Calculate engagement depth (sign-ins per user, session duration trend)
4. Project 3-month and 6-month adoption forecasts
5. Flag anomalies (sudden drops, seasonal patterns)

## Output Format
```json
{
  "trend": "growing | stable | declining",
  "trend_confidence": 0.0-1.0,
  "current_adoption_rate": 0.0,
  "avg_monthly_growth": 0.0,
  "forecast_3mo": {"users": 0, "adoption_rate": 0.0},
  "forecast_6mo": {"users": 0, "adoption_rate": 0.0},
  "engagement_score": 0.0-1.0,
  "anomalies": ["description of any anomalies"],
  "insight": "1-2 sentence summary of the key finding"
}
```""",
        "parameters": {
            "temperature": 0.15,
            "max_tokens": 1000,
            "top_p": 0.9
        },
        "tags": ["analytics", "usage", "entra-id", "trends"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Processes Entra ID sign-in analytics into trend assessments", "is_primary": True},
            {"usage_type": "page", "location": "/applications/[id]", "description": "Powers the usage trend chart and forecast on app detail pages", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Declining usage over 6 months",
                "input_data": {"app_name": "Legacy Portal", "category": "Productivity", "total_licenses": 500, "monthly_data": [{"month": "2025-10", "unique_users": 320, "total_signins": 2800, "avg_session_minutes": 22}, {"month": "2025-11", "unique_users": 290, "total_signins": 2400, "avg_session_minutes": 18}, {"month": "2025-12", "unique_users": 245, "total_signins": 1900, "avg_session_minutes": 15}, {"month": "2026-01", "unique_users": 210, "total_signins": 1500, "avg_session_minutes": 12}, {"month": "2026-02", "unique_users": 180, "total_signins": 1200, "avg_session_minutes": 10}, {"month": "2026-03", "unique_users": 155, "total_signins": 950, "avg_session_minutes": 8}]},
                "expected_output": "trend: declining",
                "notes": "Steady decline from 320 to 155 users over 6 months with shrinking session durations"
            },
        ],
    },
    {
        "id": _uuid("prompt-decision-summary"),
        "slug": "decision-summary",
        "name": "Decision Summary Generator",
        "description": "Generates a plain-language executive summary for a rationalization decision, suitable for leadership review and stakeholder communication.",
        "category": "reporting",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are a business writer creating executive summaries for IT leadership. Write in clear, non-technical language. Focus on business impact, cost implications, and recommended actions. Keep summaries concise -- leadership reads dozens of these.",
        "content": """Generate an executive summary for the following rationalization decision.

## Decision Details
- **Application:** {{app_name}} ({{vendor}})
- **Category:** {{category}}
- **Decision:** {{decision_type}} (keep/cut/replace/consolidate)
- **Status:** {{status}}
- **Submitted By:** {{submitted_by}} ({{submitter_role}})
- **Justification:** {{justification}}

## Supporting Data
- **Annual Cost:** ${{annual_cost}}
- **Active Users:** {{active_users}} of {{total_licenses}} licensed
- **Adoption Rate:** {{adoption_rate}}%
- **Estimated Savings:** ${{savings_estimate}}
- **AI Confidence Score:** {{confidence}}%
- **Vendor Risk Level:** {{vendor_risk}}

## Output Requirements
Write a 3-4 paragraph executive summary that includes:
1. **Context:** What the app does and its current state
2. **Recommendation:** The decision and why, with key data points
3. **Impact:** Financial impact, user impact, and timeline
4. **Next Steps:** What needs to happen to execute this decision""",
        "parameters": {
            "temperature": 0.4,
            "max_tokens": 800,
            "top_p": 0.95
        },
        "tags": ["reporting", "executive", "decisions"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Generates executive summaries when decisions are approved", "is_primary": True},
            {"usage_type": "page", "location": "/decisions", "description": "Displays generated summary on the decision detail view", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "CUT decision for low-adoption app",
                "input_data": {"app_name": "Evernote Business", "vendor": "Evernote", "category": "Productivity", "decision_type": "cut", "status": "approved", "submitted_by": "IT Admin", "submitter_role": "Admin", "justification": "Only 12% adoption, cheaper alternatives available", "annual_cost": 36000, "active_users": 60, "total_licenses": 500, "adoption_rate": 12.0, "savings_estimate": 36000, "confidence": 92, "vendor_risk": "medium"},
                "expected_output": "Executive summary recommending retirement of Evernote Business",
                "notes": "Should produce a clear, professional summary suitable for leadership"
            },
        ],
    },
    {
        "id": _uuid("prompt-procurement-analysis"),
        "slug": "procurement-analysis",
        "name": "Procurement Contract Analysis",
        "description": "Analyzes Workday procurement contract data to identify renewal optimization opportunities, overspend patterns, and renegotiation leverage points.",
        "category": "finance",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are a procurement analyst specializing in enterprise software contracts. You identify optimization opportunities in licensing terms, payment structures, and renewal timing. Always recommend actionable next steps with specific dollar amounts.",
        "content": """Analyze the procurement contract data for the following vendor.

## Contract Data (from Workday)
- **Vendor:** {{vendor_name}}
- **Contract Number:** {{contract_number}}
- **Annual Value:** ${{annual_value}}
- **Start Date:** {{start_date}}
- **End Date:** {{end_date}}
- **Payment Terms:** {{payment_terms}}
- **License Type:** {{license_type}}
- **Licensed Quantity:** {{licensed_qty}}
- **Auto-Renewal:** {{auto_renewal}}
- **Cancellation Notice:** {{cancellation_notice_days}} days

## Current Usage
- **Active Users:** {{active_users}}
- **Utilization:** {{utilization_pct}}%

## Analysis Requirements
1. Identify right-sizing opportunity (licensed vs actual usage)
2. Flag upcoming renewal windows and deadlines
3. Assess renegotiation leverage (utilization, market alternatives)
4. Calculate potential savings from optimization
5. Note any contractual risks (auto-renewal traps, penalty clauses)

## Output Format
```json
{
  "optimization_type": "right-size | renegotiate | consolidate | terminate",
  "current_annual_cost": 0.00,
  "optimized_annual_cost": 0.00,
  "annual_savings": 0.00,
  "action_deadline": "YYYY-MM-DD",
  "leverage_points": ["point1", "point2"],
  "risks": ["risk1", "risk2"],
  "recommended_actions": [
    {"action": "description", "deadline": "YYYY-MM-DD", "owner": "role"}
  ]
}
```""",
        "parameters": {
            "temperature": 0.15,
            "max_tokens": 1200,
            "top_p": 0.9
        },
        "tags": ["finance", "procurement", "workday", "contracts"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Analyzes Workday procurement data during data source sync", "is_primary": True},
            {"usage_type": "page", "location": "/data-sources", "description": "Surfaces contract insights on the data sources page", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Overprovisioned license with renewal approaching",
                "input_data": {"vendor_name": "Adobe", "contract_number": "WD-2024-0042", "annual_value": 240000, "start_date": "2024-01-15", "end_date": "2026-07-15", "payment_terms": "annual prepaid", "license_type": "named user", "licensed_qty": 2000, "auto_renewal": True, "cancellation_notice_days": 90, "active_users": 800, "utilization_pct": 40.0},
                "expected_output": "optimization_type: right-size, annual_savings > $100,000",
                "notes": "60% unused licenses with renewal approaching = major right-sizing opportunity"
            },
        ],
    },
    {
        "id": _uuid("prompt-submission-classifier"),
        "slug": "submission-classifier",
        "name": "Voluntary Submission Classifier",
        "description": "Classifies and enriches voluntary app submissions from department heads, matching them against the existing portfolio and suggesting initial categorization and risk flags.",
        "category": "intake",
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "source_file": "backend/app/services/ai_engine.py",
        "system_message": "You are an IT intake analyst. You process voluntary application submissions from business users, classify them accurately, and flag potential issues (shadow IT, duplicate tools, security concerns). Be efficient -- this runs on every submission.",
        "content": """Classify and enrich the following voluntary application submission.

## Submission
- **App Name:** {{submitted_app_name}}
- **Submitted By:** {{submitter_name}} ({{submitter_department}})
- **Description:** {{description}}
- **Estimated Users:** {{estimated_users}}
- **Estimated Monthly Cost:** ${{estimated_monthly_cost}}
- **Business Justification:** {{justification}}

## Existing Portfolio (for duplicate detection)
{{#each existing_apps}}
- {{name}} ({{vendor}}) -- {{category}}
{{/each}}

## Classification Requirements
1. Assign a category (from: Productivity, Security, DevOps, HR, Finance, Collaboration, Analytics, Communication, Project Management, Infrastructure, Marketing, Sales, Operations)
2. Detect potential duplicates in the existing portfolio
3. Flag security concerns (data handling, compliance implications)
4. Estimate annual cost from monthly figures
5. Assign initial priority (low/medium/high) based on user count and business justification

## Output Format
```json
{
  "category": "assigned category",
  "potential_duplicates": ["app1", "app2"],
  "is_shadow_it": true/false,
  "security_flags": ["flag1", "flag2"],
  "estimated_annual_cost": 0.00,
  "priority": "low | medium | high",
  "initial_recommendation": "review | fast-track | flag-for-security",
  "notes": "Brief analyst notes"
}
```""",
        "parameters": {
            "temperature": 0.1,
            "max_tokens": 600,
            "top_p": 0.9
        },
        "tags": ["intake", "classification", "submissions"],
        "usages": [
            {"usage_type": "service", "location": "backend/app/services/ai_engine.py", "description": "Auto-classifies new voluntary submissions on intake", "is_primary": True},
            {"usage_type": "page", "location": "/submissions", "description": "Shows classification results on the submissions list page", "is_primary": False},
        ],
        "test_cases": [
            {
                "name": "Duplicate detection for project management tool",
                "input_data": {"submitted_app_name": "Asana", "submitter_name": "Jane Smith", "submitter_department": "Marketing", "description": "Project tracking tool for marketing campaigns", "estimated_users": 15, "estimated_monthly_cost": 225, "justification": "Need better project tracking for campaign launches", "existing_apps": [{"name": "Jira", "vendor": "Atlassian", "category": "Project Management"}, {"name": "Monday.com", "vendor": "Monday", "category": "Project Management"}]},
                "expected_output": "potential_duplicates: [Jira, Monday.com]",
                "notes": "Should detect overlap with existing PM tools and flag as potential shadow IT"
            },
        ],
    },
]


def upgrade() -> None:
    # Use raw connection for bulk inserts
    conn = op.get_bind()

    for prompt in PROMPTS:
        # Insert managed_prompt
        conn.execute(
            sa.text("""
                INSERT INTO managed_prompts
                    (id, slug, name, description, category, provider, model,
                     current_version, is_active, is_locked, source_file,
                     created_by, updated_by, created_at, updated_at)
                VALUES
                    (:id, :slug, :name, :description, :category, :provider, :model,
                     1, true, false, :source_file,
                     'system', 'system', NOW(), NOW())
            """),
            {
                "id": prompt["id"],
                "slug": prompt["slug"],
                "name": prompt["name"],
                "description": prompt["description"],
                "category": prompt["category"],
                "provider": prompt["provider"],
                "model": prompt["model"],
                "source_file": prompt["source_file"],
            },
        )

        # Insert initial version (version 1)
        conn.execute(
            sa.text("""
                INSERT INTO prompt_versions
                    (id, prompt_id, version, content, system_message, parameters,
                     model, change_summary, created_by, created_at)
                VALUES
                    (:id, :prompt_id, 1, :content, :system_message, :parameters,
                     :model, 'Initial version', 'system', NOW())
            """),
            {
                "id": _uuid(f"version-{prompt['slug']}-v1"),
                "prompt_id": prompt["id"],
                "content": prompt["content"],
                "system_message": prompt["system_message"],
                "parameters": json.dumps(prompt["parameters"]),
                "model": prompt["model"],
            },
        )

        # Insert usages
        for i, usage in enumerate(prompt.get("usages", [])):
            conn.execute(
                sa.text("""
                    INSERT INTO prompt_usages
                        (id, prompt_id, usage_type, location, description, is_primary,
                         call_count, error_count, created_at, updated_at)
                    VALUES
                        (:id, :prompt_id, :usage_type, :location, :description, :is_primary,
                         :call_count, 0, NOW(), NOW())
                """),
                {
                    "id": _uuid(f"usage-{prompt['slug']}-{i}"),
                    "prompt_id": prompt["id"],
                    "usage_type": usage["usage_type"],
                    "location": usage["location"],
                    "description": usage["description"],
                    "is_primary": usage["is_primary"],
                    "call_count": 0,
                },
            )

        # Insert tags
        for tag in prompt.get("tags", []):
            conn.execute(
                sa.text("""
                    INSERT INTO prompt_tags (id, prompt_id, tag, created_at)
                    VALUES (:id, :prompt_id, :tag, NOW())
                """),
                {
                    "id": _uuid(f"tag-{prompt['slug']}-{tag}"),
                    "prompt_id": prompt["id"],
                    "tag": tag,
                },
            )

        # Insert test cases
        for j, tc in enumerate(prompt.get("test_cases", [])):
            conn.execute(
                sa.text("""
                    INSERT INTO prompt_test_cases
                        (id, prompt_id, name, input_data, expected_output, notes,
                         created_by, created_at, updated_at)
                    VALUES
                        (:id, :prompt_id, :name, :input_data, :expected_output, :notes,
                         'system', NOW(), NOW())
                """),
                {
                    "id": _uuid(f"test-{prompt['slug']}-{j}"),
                    "prompt_id": prompt["id"],
                    "name": tc["name"],
                    "input_data": json.dumps(tc["input_data"]),
                    "expected_output": tc["expected_output"],
                    "notes": tc["notes"],
                },
            )

        # Insert audit log entry for creation
        conn.execute(
            sa.text("""
                INSERT INTO prompt_audit_log
                    (id, action, prompt_id, prompt_slug, version, user_id, user_email, created_at)
                VALUES
                    (:id, 'created', :prompt_id, :slug, 1, 'system', 'system@techdebt.local', NOW())
            """),
            {
                "id": _uuid(f"audit-{prompt['slug']}-created"),
                "prompt_id": prompt["id"],
                "slug": prompt["slug"],
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    for prompt in PROMPTS:
        pid = prompt["id"]
        conn.execute(sa.text("DELETE FROM prompt_audit_log WHERE prompt_id = :pid"), {"pid": pid})
        conn.execute(sa.text("DELETE FROM prompt_test_cases WHERE prompt_id = :pid"), {"pid": pid})
        conn.execute(sa.text("DELETE FROM prompt_tags WHERE prompt_id = :pid"), {"pid": pid})
        conn.execute(sa.text("DELETE FROM prompt_usages WHERE prompt_id = :pid"), {"pid": pid})
        conn.execute(sa.text("DELETE FROM prompt_versions WHERE prompt_id = :pid"), {"pid": pid})
        conn.execute(sa.text("DELETE FROM managed_prompts WHERE id = :pid"), {"pid": pid})
