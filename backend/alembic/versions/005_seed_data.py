"""Seed data -- roles, permissions, role_permissions, users, data_sources,
applications, recommendations, decisions

Revision ID: 005
Revises: 004
Create Date: 2025-01-01 00:00:00.000000

Seeds all reference data and ~100 realistic SaaS applications for the
TechDebt rationalization dashboard.
"""
from typing import Sequence, Union

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Deterministic UUID namespace
# ---------------------------------------------------------------------------
NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _uuid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# ROLE IDs
# ---------------------------------------------------------------------------
ROLE_SUPER_ADMIN = _uuid("role-super-admin")
ROLE_ADMIN = _uuid("role-admin")
ROLE_FINANCE_REVIEWER = _uuid("role-finance-reviewer")
ROLE_DEPT_HEAD = _uuid("role-department-head")
ROLE_VIEWER = _uuid("role-viewer")

# ---------------------------------------------------------------------------
# USER IDs
# ---------------------------------------------------------------------------
USER_ADMIN = _uuid("user-mock-admin")
USER_ITADMIN = _uuid("user-mock-itadmin")
USER_FINANCE = _uuid("user-mock-finance")
USER_DEPTHEAD = _uuid("user-mock-depthead")
USER_VIEWER = _uuid("user-mock-viewer")

# ---------------------------------------------------------------------------
# DATA SOURCE IDs
# ---------------------------------------------------------------------------
DS_WORKDAY = _uuid("ds-workday")
DS_AUDITBOARD = _uuid("ds-auditboard")
DS_ENTRA = _uuid("ds-entra-id")
DS_MANUAL = _uuid("ds-voluntary-submissions")


# ---------------------------------------------------------------------------
# PERMISSION definitions  (resource, action, description)
# ---------------------------------------------------------------------------
PERMISSION_DEFS = [
    ("dashboard", "read", "View dashboard"),
    ("applications", "read", "View applications"),
    ("applications", "create", "Create applications"),
    ("applications", "update", "Update applications"),
    ("applications", "delete", "Delete applications"),
    ("recommendations", "read", "View recommendations"),
    ("recommendations", "create", "Create recommendations"),
    ("recommendations", "update", "Update recommendations"),
    ("decisions", "read", "View decisions"),
    ("decisions", "create", "Create decisions"),
    ("decisions", "update", "Update decisions"),
    ("data_sources", "read", "View data sources"),
    ("data_sources", "update", "Update data sources"),
    ("categories", "read", "View categories"),
    ("categories", "create", "Create categories"),
    ("categories", "update", "Update categories"),
    ("categories", "delete", "Delete categories"),
    ("submissions", "read", "View submissions"),
    ("submissions", "create", "Create submissions"),
    ("admin.users", "read", "View users admin"),
    ("admin.users", "create", "Create users admin"),
    ("admin.users", "update", "Update users admin"),
    ("admin.users", "delete", "Delete users admin"),
    ("admin.roles", "read", "View roles admin"),
    ("admin.roles", "create", "Create roles admin"),
    ("admin.roles", "update", "Update roles admin"),
    ("admin.roles", "delete", "Delete roles admin"),
    ("admin.settings", "read", "View settings admin"),
    ("admin.settings", "update", "Update settings admin"),
    ("admin.logs", "read", "View activity logs"),
    ("admin.logs", "delete", "Delete activity logs"),
    ("admin.prompts", "read", "View AI prompts"),
    ("admin.prompts", "create", "Create AI prompts"),
    ("admin.prompts", "update", "Update AI prompts"),
    ("admin.prompts", "delete", "Delete AI prompts"),
]

# Build a dict: (resource, action) -> uuid
PERM_IDS = {(r, a): _uuid(f"perm-{r}-{a}") for r, a, _ in PERMISSION_DEFS}

# ---------------------------------------------------------------------------
# ROLE -> PERMISSION mappings
# ---------------------------------------------------------------------------
ALL_PERMS = list(PERM_IDS.keys())

ADMIN_PERMS = [
    p for p in ALL_PERMS
    if not (p[0] in ("admin.users", "admin.roles", "admin.prompts") and p[1] in ("create", "update", "delete"))
]

FINANCE_PERMS = [
    ("dashboard", "read"),
    ("applications", "read"),
    ("recommendations", "read"),
    ("recommendations", "create"),
    ("recommendations", "update"),
    ("decisions", "read"),
    ("decisions", "create"),
    ("decisions", "update"),
    ("data_sources", "read"),
    ("submissions", "read"),
]

DEPT_HEAD_PERMS = [
    ("dashboard", "read"),
    ("applications", "read"),
    ("recommendations", "read"),
    ("decisions", "read"),
    ("decisions", "create"),
    ("submissions", "read"),
    ("submissions", "create"),
]

VIEWER_PERMS = [
    ("dashboard", "read"),
    ("applications", "read"),
    ("recommendations", "read"),
    ("decisions", "read"),
    ("submissions", "read"),
]

ROLE_PERM_MAP = {
    ROLE_SUPER_ADMIN: ALL_PERMS,
    ROLE_ADMIN: ADMIN_PERMS,
    ROLE_FINANCE_REVIEWER: FINANCE_PERMS,
    ROLE_DEPT_HEAD: DEPT_HEAD_PERMS,
    ROLE_VIEWER: VIEWER_PERMS,
}

# ---------------------------------------------------------------------------
# APPLICATION data (100 apps)
# ---------------------------------------------------------------------------
# (name, vendor, category, app_type, status, annual_cost, cost_per_license,
#  total_licenses, active_users, department, data_source, risk_score,
#  compliance_status, contract_end)
# adoption_rate is calculated
APPS = [
    # ---- Productivity (10) ----
    ("Microsoft 365", "Microsoft", "Productivity", "saas", "active", 1800000, 35, 5000, 4800, "All Departments", "workday", 5, "compliant", "2027-06-30"),
    ("Google Workspace", "Google", "Productivity", "saas", "under_review", 420000, 14, 2500, 580, "Marketing", "workday", 25, "compliant", "2025-09-15"),
    ("Notion", "Notion Labs", "Productivity", "saas", "active", 96000, 10, 800, 720, "Engineering", "manual", 10, "compliant", "2026-12-01"),
    ("Confluence", "Atlassian", "Productivity", "saas", "under_review", 54000, 7.50, 600, 145, "Engineering", "workday", 30, "pending_review", "2025-04-30"),
    ("Evernote Business", "Evernote", "Productivity", "saas", "deprecated", 18000, 15, 100, 8, "Sales", "manual", 65, "non_compliant", "2024-12-31"),
    ("Coda", "Coda", "Productivity", "saas", "active", 36000, 12, 250, 210, "Engineering", "manual", 12, "compliant", None),
    ("Quip", "Salesforce", "Productivity", "saas", "deprecated", 24000, 10, 200, 15, "Sales", "workday", 55, "non_compliant", "2024-06-30"),
    ("Dropbox Paper", "Dropbox", "Productivity", "saas", "under_review", 15000, 12.50, 100, 22, "Marketing", "manual", 40, "pending_review", "2025-08-01"),
    ("Zoho Workplace", "Zoho", "Productivity", "saas", "active", 12000, 5, 200, 180, "Operations", "manual", 8, "compliant", "2026-03-15"),
    ("LibreOffice Enterprise", "Collabora", "Productivity", "cots", "cut", 8000, 5, 150, 0, "IT", "manual", None, None, "2024-01-15"),

    # ---- Security (10) ----
    ("CrowdStrike Falcon", "CrowdStrike", "Security", "saas", "active", 480000, 18, 5000, 5000, "Security", "auditboard", 3, "compliant", "2026-11-30"),
    ("Palo Alto Prisma", "Palo Alto Networks", "Security", "saas", "active", 360000, 25, 1200, 1150, "Security", "auditboard", 5, "compliant", "2027-01-31"),
    ("Splunk Enterprise", "Splunk", "Security", "cots", "active", 750000, 60, 500, 320, "Security", "workday", 8, "compliant", "2026-08-15"),
    ("Tenable.io", "Tenable", "Security", "saas", "active", 180000, 15, 1000, 950, "Security", "auditboard", 4, "compliant", "2026-06-30"),
    ("Qualys VMDR", "Qualys", "Security", "saas", "under_review", 120000, 12, 800, 200, "Security", "auditboard", 35, "pending_review", "2025-07-31"),
    ("Rapid7 InsightVM", "Rapid7", "Security", "saas", "under_review", 96000, 10, 800, 180, "Security", "auditboard", 38, "pending_review", "2025-10-15"),
    ("Snyk", "Snyk", "Security", "saas", "active", 72000, 30, 200, 195, "Engineering", "manual", 6, "compliant", "2026-09-01"),
    ("Wiz", "Wiz", "Security", "saas", "active", 240000, 40, 500, 480, "Security", "auditboard", 4, "compliant", "2027-03-31"),
    ("Darktrace", "Darktrace", "Security", "saas", "under_review", 300000, 50, 500, 120, "Security", "auditboard", 42, "non_compliant", "2025-05-31"),
    ("Carbon Black", "VMware", "Security", "saas", "deprecated", 96000, 12, 600, 45, "Security", "auditboard", 60, "non_compliant", "2024-09-30"),

    # ---- DevOps (10) ----
    ("GitHub Enterprise", "GitHub", "DevOps", "saas", "active", 252000, 21, 1000, 980, "Engineering", "entra_id", 3, "compliant", "2027-02-28"),
    ("Jira Software", "Atlassian", "DevOps", "saas", "active", 120000, 10, 1000, 850, "Engineering", "workday", 8, "compliant", "2026-10-31"),
    ("GitLab Ultimate", "GitLab", "DevOps", "saas", "under_review", 180000, 30, 500, 95, "Engineering", "manual", 40, "pending_review", "2025-06-15"),
    ("Jenkins (CloudBees)", "CloudBees", "DevOps", "cots", "under_review", 150000, 50, 250, 60, "Engineering", "manual", 55, "non_compliant", "2025-03-31"),
    ("CircleCI", "CircleCI", "DevOps", "saas", "active", 48000, 20, 200, 185, "Engineering", "manual", 10, "compliant", "2026-07-31"),
    ("Datadog", "Datadog", "DevOps", "saas", "active", 360000, 30, 1000, 920, "Engineering", "workday", 5, "compliant", "2027-04-30"),
    ("PagerDuty", "PagerDuty", "DevOps", "saas", "active", 84000, 35, 200, 195, "Engineering", "workday", 6, "compliant", "2026-05-15"),
    ("Terraform Cloud", "HashiCorp", "DevOps", "saas", "active", 42000, 70, 50, 48, "Engineering", "manual", 7, "compliant", "2026-12-31"),
    ("New Relic", "New Relic", "DevOps", "saas", "under_review", 240000, 40, 500, 110, "Engineering", "workday", 45, "pending_review", "2025-08-31"),
    ("Bamboo", "Atlassian", "DevOps", "saas", "deprecated", 36000, 12, 250, 18, "Engineering", "workday", 70, "non_compliant", "2024-03-31"),

    # ---- HR (10) ----
    ("Workday HCM", "Workday", "HR", "saas", "active", 2500000, 45, 5000, 4950, "HR", "workday", 2, "compliant", "2027-12-31"),
    ("BambooHR", "BambooHR", "HR", "saas", "under_review", 60000, 8, 600, 150, "HR", "workday", 35, "pending_review", "2025-09-30"),
    ("ADP Workforce Now", "ADP", "HR", "saas", "active", 180000, 12, 1200, 1200, "HR", "workday", 3, "compliant", "2026-06-30"),
    ("Greenhouse", "Greenhouse", "HR", "saas", "active", 96000, 40, 200, 190, "HR", "workday", 5, "compliant", "2026-11-30"),
    ("Lever", "Lever", "HR", "saas", "under_review", 72000, 30, 200, 45, "HR", "workday", 48, "pending_review", "2025-07-15"),
    ("Culture Amp", "Culture Amp", "HR", "saas", "active", 54000, 5, 900, 800, "HR", "manual", 8, "compliant", "2026-08-31"),
    ("15Five", "15Five", "HR", "saas", "active", 30000, 7, 350, 310, "HR", "manual", 10, "compliant", "2026-04-15"),
    ("Lattice", "Lattice", "HR", "saas", "under_review", 48000, 8, 500, 120, "HR", "manual", 42, "pending_review", "2025-11-30"),
    ("Paycom", "Paycom", "HR", "cots", "active", 200000, 15, 1100, 1100, "HR", "workday", 4, "compliant", "2027-03-31"),
    ("Namely", "Namely", "HR", "saas", "deprecated", 36000, 12, 250, 20, "HR", "workday", 62, "non_compliant", "2024-08-31"),

    # ---- Finance (10) ----
    ("SAP Concur", "SAP", "Finance", "saas", "active", 600000, 25, 2000, 1850, "Finance", "workday", 6, "compliant", "2027-01-31"),
    ("NetSuite", "Oracle", "Finance", "saas", "active", 480000, 80, 500, 490, "Finance", "workday", 4, "compliant", "2027-06-30"),
    ("Coupa", "Coupa", "Finance", "saas", "active", 360000, 60, 500, 480, "Finance", "workday", 5, "compliant", "2026-12-31"),
    ("Expensify", "Expensify", "Finance", "saas", "under_review", 72000, 6, 1000, 280, "Finance", "workday", 30, "pending_review", "2025-10-31"),
    ("Bill.com", "Bill.com", "Finance", "saas", "active", 24000, 40, 50, 48, "Finance", "manual", 8, "compliant", "2026-09-15"),
    ("Brex", "Brex", "Finance", "saas", "active", 18000, 15, 100, 95, "Finance", "manual", 5, "compliant", "2026-07-31"),
    ("Tipalti", "Tipalti", "Finance", "saas", "under_review", 96000, 40, 200, 50, "Finance", "workday", 45, "pending_review", "2025-06-30"),
    ("Avalara", "Avalara", "Finance", "saas", "active", 42000, 35, 100, 100, "Finance", "workday", 6, "compliant", "2026-11-15"),
    ("BlackLine", "BlackLine", "Finance", "saas", "active", 144000, 120, 100, 95, "Finance", "workday", 7, "compliant", "2027-02-28"),
    ("Sage Intacct", "Sage", "Finance", "saas", "cut", 108000, 90, 100, 10, "Finance", "workday", 72, "non_compliant", "2024-05-31"),

    # ---- Collaboration (10) ----
    ("Slack", "Salesforce", "Collaboration", "saas", "active", 600000, 12.50, 4000, 3800, "All Departments", "entra_id", 4, "compliant", "2027-03-31"),
    ("Microsoft Teams", "Microsoft", "Collaboration", "saas", "active", 0, 0, 5000, 4900, "All Departments", "entra_id", 2, "compliant", "2027-06-30"),
    ("Miro", "Miro", "Collaboration", "saas", "active", 96000, 16, 500, 380, "Engineering", "manual", 12, "compliant", "2026-10-15"),
    ("Figma", "Figma", "Collaboration", "saas", "active", 120000, 15, 600, 550, "Engineering", "manual", 5, "compliant", "2026-09-30"),
    ("Lucidchart", "Lucid Software", "Collaboration", "saas", "under_review", 48000, 10, 400, 85, "Engineering", "manual", 38, "pending_review", "2025-08-15"),
    ("Mural", "Mural", "Collaboration", "saas", "under_review", 36000, 12, 250, 55, "Marketing", "manual", 42, "pending_review", "2025-07-31"),
    ("Loom", "Loom", "Collaboration", "saas", "active", 30000, 12.50, 200, 175, "All Departments", "manual", 10, "compliant", "2026-06-30"),
    ("Webex", "Cisco", "Collaboration", "saas", "deprecated", 180000, 15, 1000, 60, "All Departments", "workday", 68, "non_compliant", "2024-04-30"),
    ("BlueJeans", "Verizon", "Collaboration", "saas", "cut", 48000, 16, 250, 5, "Operations", "workday", 80, "non_compliant", "2024-02-28"),
    ("Basecamp", "37signals", "Collaboration", "saas", "under_review", 6000, 11, 50, 12, "Marketing", "manual", 30, "pending_review", "2025-12-31"),

    # ---- Analytics (10) ----
    ("Tableau", "Salesforce", "Analytics", "saas", "active", 360000, 70, 500, 420, "All Departments", "workday", 8, "compliant", "2026-12-31"),
    ("Power BI Pro", "Microsoft", "Analytics", "saas", "active", 120000, 10, 1000, 850, "All Departments", "entra_id", 5, "compliant", "2027-06-30"),
    ("Looker", "Google", "Analytics", "saas", "under_review", 240000, 60, 300, 75, "Engineering", "workday", 50, "pending_review", "2025-09-30"),
    ("Domo", "Domo", "Analytics", "saas", "under_review", 300000, 100, 250, 55, "Finance", "workday", 58, "non_compliant", "2025-04-15"),
    ("Sisense", "Sisense", "Analytics", "saas", "deprecated", 180000, 75, 200, 30, "Engineering", "workday", 65, "non_compliant", "2024-07-31"),
    ("Mode Analytics", "ThoughtSpot", "Analytics", "saas", "active", 48000, 40, 100, 88, "Engineering", "manual", 10, "compliant", "2026-08-15"),
    ("Amplitude", "Amplitude", "Analytics", "saas", "active", 72000, 30, 200, 190, "Engineering", "manual", 6, "compliant", "2026-10-31"),
    ("Mixpanel", "Mixpanel", "Analytics", "saas", "under_review", 60000, 25, 200, 50, "Marketing", "manual", 40, "pending_review", "2025-11-30"),
    ("Heap", "Contentsquare", "Analytics", "saas", "active", 36000, 30, 100, 90, "Engineering", "manual", 8, "compliant", "2026-07-15"),
    ("Chartio", "Atlassian", "Analytics", "saas", "cut", 24000, 20, 100, 0, "Engineering", "manual", None, None, "2023-12-31"),

    # ---- Communication (10) ----
    ("Zoom", "Zoom", "Communication", "saas", "active", 240000, 15, 3000, 2800, "All Departments", "entra_id", 5, "compliant", "2027-01-31"),
    ("Twilio", "Twilio", "Communication", "saas", "active", 144000, 0.01, 5000, 4500, "Engineering", "workday", 8, "compliant", "2026-12-15"),
    ("SendGrid", "Twilio", "Communication", "saas", "active", 36000, 15, 200, 190, "Marketing", "workday", 6, "compliant", "2026-09-30"),
    ("Mailchimp", "Intuit", "Communication", "saas", "active", 18000, 15, 100, 90, "Marketing", "manual", 10, "compliant", "2026-06-30"),
    ("Intercom", "Intercom", "Communication", "saas", "active", 84000, 70, 100, 95, "Sales", "manual", 7, "compliant", "2026-11-15"),
    ("Zendesk", "Zendesk", "Communication", "saas", "active", 180000, 30, 500, 460, "Operations", "workday", 5, "compliant", "2027-02-28"),
    ("Freshdesk", "Freshworks", "Communication", "saas", "under_review", 48000, 16, 250, 60, "Operations", "workday", 40, "pending_review", "2025-08-31"),
    ("Front", "Front", "Communication", "saas", "under_review", 60000, 25, 200, 50, "Sales", "manual", 45, "pending_review", "2025-10-15"),
    ("RingCentral", "RingCentral", "Communication", "saas", "under_review", 96000, 20, 400, 100, "All Departments", "workday", 48, "pending_review", "2025-05-31"),
    ("Vonage", "Vonage", "Communication", "saas", "deprecated", 72000, 18, 300, 25, "Sales", "workday", 62, "non_compliant", "2024-11-30"),

    # ---- Project Management (10) ----
    ("Asana", "Asana", "Project Management", "saas", "active", 108000, 12, 750, 680, "All Departments", "entra_id", 8, "compliant", "2026-11-30"),
    ("Monday.com", "monday.com", "Project Management", "saas", "active", 84000, 14, 500, 450, "Marketing", "entra_id", 7, "compliant", "2026-10-15"),
    ("Smartsheet", "Smartsheet", "Project Management", "saas", "under_review", 72000, 30, 200, 55, "Operations", "workday", 45, "pending_review", "2025-09-15"),
    ("Wrike", "Citrix", "Project Management", "saas", "under_review", 54000, 18, 250, 60, "Marketing", "workday", 42, "pending_review", "2025-07-31"),
    ("ClickUp", "ClickUp", "Project Management", "saas", "active", 42000, 7, 500, 430, "Engineering", "manual", 10, "compliant", "2026-08-31"),
    ("Trello", "Atlassian", "Project Management", "saas", "active", 12000, 5, 200, 120, "All Departments", "entra_id", 15, "compliant", "2026-05-15"),
    ("Airtable", "Airtable", "Project Management", "saas", "active", 60000, 20, 250, 230, "Operations", "manual", 8, "compliant", "2026-09-30"),
    ("Teamwork", "Teamwork", "Project Management", "saas", "deprecated", 24000, 10, 200, 15, "Operations", "workday", 58, "non_compliant", "2024-06-30"),
    ("Planview", "Planview", "Project Management", "cots", "under_review", 180000, 150, 100, 20, "IT", "workday", 65, "non_compliant", "2025-04-30"),
    ("Clarizen", "Planview", "Project Management", "saas", "cut", 96000, 80, 100, 5, "IT", "workday", 78, "non_compliant", "2024-01-31"),

    # ---- Infrastructure (10) ----
    ("AWS", "Amazon", "Infrastructure", "saas", "active", 2400000, 0, 1000, 950, "Engineering", "workday", 3, "compliant", "2027-06-30"),
    ("Azure", "Microsoft", "Infrastructure", "saas", "active", 1200000, 0, 800, 780, "Engineering", "workday", 4, "compliant", "2027-06-30"),
    ("Cloudflare", "Cloudflare", "Infrastructure", "saas", "active", 60000, 0, 500, 500, "Engineering", "manual", 3, "compliant", "2026-12-31"),
    ("Akamai", "Akamai", "Infrastructure", "saas", "under_review", 180000, 0, 200, 45, "Engineering", "workday", 50, "pending_review", "2025-06-30"),
    ("Fastly", "Fastly", "Infrastructure", "saas", "under_review", 96000, 0, 150, 30, "Engineering", "workday", 48, "pending_review", "2025-09-30"),
    ("Snowflake", "Snowflake", "Infrastructure", "saas", "active", 480000, 0, 300, 280, "Engineering", "workday", 5, "compliant", "2026-11-30"),
    ("MongoDB Atlas", "MongoDB", "Infrastructure", "saas", "active", 120000, 0, 200, 190, "Engineering", "manual", 6, "compliant", "2026-08-15"),
    ("Redis Cloud", "Redis", "Infrastructure", "saas", "active", 36000, 0, 100, 95, "Engineering", "manual", 5, "compliant", "2026-07-31"),
    ("Elastic Cloud", "Elastic", "Infrastructure", "saas", "active", 96000, 0, 150, 140, "Engineering", "manual", 7, "compliant", "2026-10-15"),
    ("VMware vSphere", "Broadcom", "Infrastructure", "cots", "under_review", 360000, 150, 200, 80, "IT", "workday", 55, "non_compliant", "2025-05-31"),
]

# Compute app IDs deterministically
APP_IDS = {app[0]: _uuid(f"app-{app[0].lower().replace(' ', '-')}") for app in APPS}

# ---------------------------------------------------------------------------
# RECOMMENDATIONS (~60)
# ---------------------------------------------------------------------------
# (app_name, recommendation_type, confidence, reasoning, cost_savings, alternative, status)
RECOMMENDATIONS = [
    # ---- KEEP (15) ----
    ("Microsoft 365", "keep", 96, "96% adoption across all departments with critical productivity dependencies. Cost per user is competitive at $35/month. No viable alternative at this scale.", None, None, "accepted"),
    ("CrowdStrike Falcon", "keep", 95, "100% endpoint coverage is mandatory for security compliance. CrowdStrike consistently ranks #1 in EDR evaluations. Switching cost would be enormous.", None, None, "accepted"),
    ("GitHub Enterprise", "keep", 94, "98% developer adoption with deep CI/CD integration. Central to engineering workflow. Migration to alternatives would cause months of disruption.", None, None, "pending"),
    ("Workday HCM", "keep", 97, "Core HR system of record with 99% adoption. Deeply integrated with payroll, benefits, and compliance reporting. Irreplaceable at current scale.", None, None, "accepted"),
    ("Slack", "keep", 92, "95% adoption as primary communication platform. Extensive bot and workflow integrations. Teams overlap creates redundancy but Slack remains the engineering default.", None, None, "pending"),
    ("Datadog", "keep", 93, "92% adoption among engineering teams. Comprehensive observability covering APM, logs, and infrastructure. Contract is competitively priced.", None, None, "pending"),
    ("SAP Concur", "keep", 90, "92.5% adoption for expense management. Integrated with ERP and corporate card programs. Switching would disrupt reimbursement workflows.", None, None, "pending"),
    ("Zoom", "keep", 91, "93% adoption across all departments. Reliable video conferencing with strong recording and webinar features. Well-integrated with calendar systems.", None, None, "pending"),
    ("Asana", "keep", 88, "91% adoption in project management. Strong cross-department usage with good template library. Cost is reasonable at $12/user/month.", None, None, "pending"),
    ("NetSuite", "keep", 94, "98% adoption in finance as core ERP. Handles GL, AP, AR, and financial reporting. Deeply embedded in financial close processes.", None, None, "accepted"),
    ("Figma", "keep", 92, "92% adoption among design and engineering teams. Industry standard for collaborative design. No viable alternative offers the same real-time collaboration.", None, None, "pending"),
    ("Snowflake", "keep", 91, "93% adoption for data warehousing. Central to analytics pipeline. Performance and scalability justify the cost.", None, None, "pending"),
    ("PagerDuty", "keep", 93, "97.5% adoption for incident management. Critical for on-call rotations and SLA tracking. Deeply integrated with monitoring tools.", None, None, "pending"),
    ("Coupa", "keep", 90, "96% adoption for procurement. Integrated with AP workflows and supplier management. Switching would disrupt procurement processes.", None, None, "pending"),
    ("Tenable.io", "keep", 89, "95% coverage for vulnerability management. Strong compliance reporting. Audit-required tool with no gaps in scanning.", None, None, "pending"),

    # ---- CUT (20) ----
    ("Evernote Business", "cut", 92, "Only 8% adoption (8 of 100 users). Annual cost of $18K for a tool that Notion and Confluence already replace. Contract expired Dec 2024.", 18000, None, "accepted"),
    ("Quip", "cut", 90, "7.5% adoption (15 of 200 users). Salesforce-bundled but unused. Confluence and Notion cover all collaborative document needs.", 24000, None, "pending"),
    ("LibreOffice Enterprise", "cut", 95, "0% active users. Microsoft 365 is the standard productivity suite. License expired Jan 2024 and no one noticed.", 8000, None, "accepted"),
    ("Carbon Black", "cut", 88, "7.5% adoption with CrowdStrike already deployed as primary EDR. Redundant security tool with expired contract.", 96000, None, "pending"),
    ("Bamboo", "cut", 91, "7.2% adoption. GitHub Actions and CircleCI have replaced all CI/CD pipelines. No active builds running on Bamboo since Q2 2024.", 36000, None, "accepted"),
    ("Namely", "cut", 87, "8% adoption. Workday HCM is the system of record. Namely was kept for a subsidiary that has since been migrated.", 36000, None, "pending"),
    ("Webex", "cut", 93, "6% adoption (60 of 1000 users) while Zoom has 93% adoption. Complete functional overlap. Contract expired April 2024.", 180000, None, "accepted"),
    ("BlueJeans", "cut", 96, "2% adoption (5 of 250 users). Third video conferencing tool behind Zoom and Teams. No unique functionality.", 48000, None, "accepted"),
    ("Sisense", "cut", 86, "15% adoption with Tableau and Power BI covering all analytics needs. High cost at $75/user/month for a tertiary tool.", 180000, None, "pending"),
    ("Chartio", "cut", 98, "0% active users. Service was acquired by Atlassian and shut down. Licenses are being paid for a non-functional product.", 24000, None, "accepted"),
    ("Teamwork", "cut", 89, "7.5% adoption. Asana and Monday.com have absorbed all project management workflows. No active projects in Teamwork.", 24000, None, "pending"),
    ("Clarizen", "cut", 91, "5% adoption (5 of 100 users). Replaced by Planview (same vendor acquired Clarizen). Paying for both.", 96000, None, "pending"),
    ("Sage Intacct", "cut", 88, "10% adoption. NetSuite handles all accounting needs. Sage was kept for a legacy integration that was decommissioned Q3 2024.", 108000, None, "pending"),
    ("Vonage", "cut", 85, "8.3% adoption. Twilio handles all communication APIs. RingCentral provides phone service. Vonage is fully redundant.", 72000, None, "pending"),
    ("Dropbox Paper", "cut", 87, "22% adoption and declining. Notion and Confluence provide superior document collaboration. Users have self-migrated.", 15000, None, "pending"),
    ("Domo", "cut", 84, "22% adoption at $100/user/month -- highest cost-per-user in analytics. Power BI and Tableau deliver equivalent dashboards at a fraction of the cost.", 300000, None, "pending"),
    ("Google Workspace", "cut", 82, "23% adoption while Microsoft 365 has 96% adoption. Maintained for a small marketing team that could easily migrate. Annual savings of $420K.", 420000, None, "deferred"),
    ("Lever", "cut", 83, "22.5% adoption. Greenhouse is the primary ATS with 95% adoption. Lever was kept for one recruiting team that has since consolidated.", 72000, None, "pending"),
    ("Darktrace", "cut", 80, "24% adoption at $300K/year. Network detection capabilities overlap with Palo Alto Prisma and CrowdStrike. High cost for marginal incremental value.", 300000, None, "deferred"),
    ("Basecamp", "cut", 78, "24% adoption. Minimal usage (12 of 50 users) at low cost, but adds to tool sprawl. Asana covers all use cases.", 6000, None, "pending"),

    # ---- REPLACE (15) ----
    ("Confluence", "replace", 82, "24% adoption despite 600 licenses. Notion has 90% adoption in engineering at lower cost. Migration path is well-documented.", 30000, "Notion", "pending"),
    ("Qualys VMDR", "replace", 79, "25% adoption vs Tenable.io at 95%. Consolidating to Tenable reduces vendor complexity and saves on duplicate scanning infrastructure.", 60000, "Tenable.io", "pending"),
    ("Rapid7 InsightVM", "replace", 78, "22.5% adoption. Third vulnerability scanner alongside Tenable and Qualys. Tenable provides superior coverage at lower per-asset cost.", 48000, "Tenable.io", "pending"),
    ("GitLab Ultimate", "replace", 81, "19% adoption while GitHub Enterprise has 98%. Engineering teams have standardized on GitHub. GitLab is maintained for 3 legacy pipelines easily migrated.", 120000, "GitHub Enterprise", "rejected"),
    ("Jenkins (CloudBees)", "replace", 77, "24% adoption with contract expiring. GitHub Actions covers all CI/CD needs. Remaining Jenkins jobs are straightforward to migrate.", 120000, "GitHub Actions", "pending"),
    ("BambooHR", "replace", 80, "25% adoption. Workday HCM handles core HR. BambooHR was used for a division that has been integrated. Migrate remaining users to Workday.", 48000, "Workday HCM", "pending"),
    ("Freshdesk", "replace", 76, "24% adoption while Zendesk has 92%. Duplicate helpdesk functionality. Zendesk has stronger analytics and automation capabilities.", 48000, "Zendesk", "pending"),
    ("Front", "replace", 74, "25% adoption. Email management features overlap with Zendesk and Intercom. Consolidating to Zendesk simplifies the support stack.", 36000, "Zendesk", "pending"),
    ("RingCentral", "replace", 72, "25% adoption. Zoom Phone provides equivalent VoIP functionality at lower cost with better integration into existing Zoom infrastructure.", 48000, "Zoom Phone", "pending"),
    ("New Relic", "replace", 75, "22% adoption while Datadog has 92%. Overlapping APM and infrastructure monitoring. Datadog provides unified observability at better per-host pricing.", 180000, "Datadog", "rejected"),
    ("Akamai", "replace", 73, "22.5% adoption. Cloudflare provides equivalent CDN and security edge capabilities at 60% lower cost with simpler configuration.", 120000, "Cloudflare", "pending"),
    ("Fastly", "replace", 71, "20% adoption alongside Cloudflare. CDN consolidation to Cloudflare would eliminate vendor complexity.", 60000, "Cloudflare", "pending"),
    ("VMware vSphere", "replace", 70, "40% adoption but Broadcom acquisition has tripled licensing costs. AWS and Azure provide equivalent compute at predictable pricing.", 200000, "AWS/Azure", "deferred"),
    ("Expensify", "replace", 76, "28% adoption while SAP Concur has 92.5%. Duplicate expense management tool maintained for a subsidiary now integrated.", 48000, "SAP Concur", "pending"),
    ("Lattice", "replace", 74, "24% adoption. Culture Amp and 15Five cover performance management with higher adoption. Consolidation reduces HR tool sprawl.", 30000, "Culture Amp", "pending"),

    # ---- CONSOLIDATE (10) ----
    ("Lucidchart", "consolidate", 75, "21% adoption. Diagramming needs overlap with Miro (76% adoption) and Figma. Consolidating to Miro for whiteboarding and Figma for technical diagrams.", 30000, "Miro + Figma", "pending"),
    ("Mural", "consolidate", 74, "22% adoption. Virtual whiteboard functionality fully duplicated by Miro at higher adoption. Both teams could consolidate.", 24000, "Miro", "pending"),
    ("Smartsheet", "consolidate", 72, "27.5% adoption. Project tracking duplicated by Asana (91%) and Airtable (92%). Spreadsheet-style PM can be handled by Airtable.", 48000, "Airtable", "pending"),
    ("Wrike", "consolidate", 71, "24% adoption. Fourth project management tool alongside Asana, Monday.com, and ClickUp. Marketing team should standardize on Monday.com.", 36000, "Monday.com", "pending"),
    ("Looker", "consolidate", 73, "25% adoption alongside Tableau (84%) and Power BI (85%). Three BI tools is excessive. Looker's SQL-based approach overlaps with Tableau.", 180000, "Tableau + Power BI", "pending"),
    ("Mixpanel", "consolidate", 70, "25% adoption alongside Amplitude (95%). Product analytics tools with identical feature sets. Amplitude has broader adoption and lower cost.", 36000, "Amplitude", "pending"),
    ("Splunk Enterprise", "consolidate", 68, "64% adoption but $750K/year is highest security spend. Datadog Log Management covers most use cases at a fraction of the cost. Keep Splunk for SIEM only.", 400000, "Datadog (logs) + Splunk (SIEM)", "rejected"),
    ("Microsoft Teams", "consolidate", 65, "98% adoption but functional overlap with Slack (95%). Both are enterprise-licensed. Recommendation to standardize on one reduces context-switching.", None, "Slack or Teams (choose one)", "deferred"),
    ("Trello", "consolidate", 72, "60% adoption but extremely lightweight vs Asana. Most Trello boards could migrate to Asana with minimal disruption.", 8000, "Asana", "pending"),
    ("Loom", "consolidate", 68, "87.5% adoption but async video features now available in Zoom Clips. As Zoom Clips matures, Loom becomes redundant.", 15000, "Zoom Clips", "pending"),
]

REC_IDS = {f"{r[0]}-{r[1]}": _uuid(f"rec-{r[0].lower().replace(' ', '-')}-{r[1]}") for r in RECOMMENDATIONS}

# ---------------------------------------------------------------------------
# DECISIONS (~15)
# ---------------------------------------------------------------------------
# (app_name, rec_type, decision_type, justification, submitted_by_uuid, status,
#  reviewer_uuid_or_none, cost_impact)
DECISIONS = [
    ("Evernote Business", "cut", "cut", "Approved by IT governance board. All 8 remaining users migrated to Notion. Contract will not be renewed.", USER_ADMIN, "approved", USER_FINANCE, -18000),
    ("LibreOffice Enterprise", "cut", "cut", "No active users. License already expired. Removing from vendor list.", USER_ITADMIN, "approved", USER_ADMIN, -8000),
    ("Webex", "cut", "cut", "Approved for decommission. Zoom is the enterprise standard. 60 remaining users notified of migration deadline.", USER_ADMIN, "approved", USER_FINANCE, -180000),
    ("BlueJeans", "cut", "cut", "Immediate cut approved. 5 remaining users moved to Zoom. No business impact.", USER_ITADMIN, "approved", USER_ADMIN, -48000),
    ("Chartio", "cut", "cut", "Product no longer exists. Removing billing entry from procurement system.", USER_ITADMIN, "approved", USER_ADMIN, -24000),
    ("Bamboo", "cut", "cut", "All CI/CD pipelines migrated to GitHub Actions. Atlassian confirmed contract termination.", USER_ITADMIN, "approved", USER_FINANCE, -36000),
    ("Carbon Black", "cut", "cut", "CrowdStrike provides complete EDR coverage. VMware notified of non-renewal.", USER_ADMIN, "approved", USER_FINANCE, -96000),
    ("Google Workspace", "cut", "keep", "Marketing team requires Google Workspace for agency collaboration. Reducing to 500 licenses instead of 2500. Renegotiating contract.", USER_DEPTHEAD, "approved", USER_FINANCE, -336000),
    ("Confluence", "replace", "replace", "Migration to Notion approved. Engineering team to complete migration by Q3 2025. Atlassian license count reduced.", USER_ITADMIN, "pending_review", None, -30000),
    ("GitLab Ultimate", "replace", "keep", "DevSecOps team requires GitLab SAST/DAST features not available in GitHub. Reducing to 100 licenses for security scanning only.", USER_ADMIN, "approved", USER_ITADMIN, -120000),
    ("Darktrace", "cut", "defer", "Security team requests 6-month evaluation period to validate Palo Alto provides equivalent network detection. Decision deferred to Q4 2025.", USER_DEPTHEAD, "pending_review", None, 0),
    ("Splunk Enterprise", "consolidate", "keep", "CISO mandate: Splunk remains SIEM of record. Negotiating volume discount. Datadog handles application logs only.", USER_ADMIN, "approved", USER_FINANCE, -200000),
    ("VMware vSphere", "replace", "defer", "Cloud migration in progress but 40% of workloads cannot move to public cloud due to data residency requirements. Reassess after hybrid cloud architecture review.", USER_DEPTHEAD, "pending_review", None, 0),
    ("Domo", "cut", "cut", "Finance team agrees Power BI meets all dashboard needs. 55 Domo users to be trained on Power BI by Q2 2025.", USER_FINANCE, "pending_review", None, -300000),
    ("New Relic", "replace", "replace", "Engineering approved Datadog consolidation. New Relic contract expires Aug 2025. Migration plan in progress.", USER_ITADMIN, "pending_review", None, -180000),
]


# ===================================================================
# upgrade
# ===================================================================
def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. ROLES
    # ---------------------------------------------------------------
    op.execute(sa.text(
        f"INSERT INTO roles (id, name, description, is_system) VALUES "
        f"('{ROLE_SUPER_ADMIN}', 'Super Admin', 'Full system access', true), "
        f"('{ROLE_ADMIN}', 'Admin', 'IT Asset Management administrator', true), "
        f"('{ROLE_FINANCE_REVIEWER}', 'Finance Reviewer', 'Reviews costs and financial impact of application decisions', true), "
        f"('{ROLE_DEPT_HEAD}', 'Department Head', 'Submits and reviews decisions for their department', true), "
        f"('{ROLE_VIEWER}', 'Viewer', 'Read-only access to dashboards and reports', true)"
    ))

    # ---------------------------------------------------------------
    # 2. PERMISSIONS
    # ---------------------------------------------------------------
    perm_values = ", ".join(
        f"('{PERM_IDS[(r, a)]}', '{r}', '{a}', '{d}')"
        for r, a, d in PERMISSION_DEFS
    )
    op.execute(sa.text(
        f"INSERT INTO permissions (id, resource, action, description) VALUES {perm_values}"
    ))

    # ---------------------------------------------------------------
    # 3. ROLE-PERMISSION MAPPINGS
    # ---------------------------------------------------------------
    rp_values = ", ".join(
        f"('{role_id}', '{PERM_IDS[perm]}')"
        for role_id, perms in ROLE_PERM_MAP.items()
        for perm in perms
    )
    op.execute(sa.text(
        f"INSERT INTO role_permissions (role_id, permission_id) VALUES {rp_values}"
    ))

    # ---------------------------------------------------------------
    # 4. USERS
    # ---------------------------------------------------------------
    users = [
        (USER_ADMIN, "mock-admin", "admin@techdebt.local", "Admin User", ROLE_SUPER_ADMIN),
        (USER_ITADMIN, "mock-itadmin", "itadmin@techdebt.local", "IT Admin", ROLE_ADMIN),
        (USER_FINANCE, "mock-finance", "finance@techdebt.local", "Finance Reviewer", ROLE_FINANCE_REVIEWER),
        (USER_DEPTHEAD, "mock-depthead", "depthead@techdebt.local", "Department Head", ROLE_DEPT_HEAD),
        (USER_VIEWER, "mock-viewer", "viewer@techdebt.local", "Viewer User", ROLE_VIEWER),
    ]
    user_values = ", ".join(
        f"('{uid}', '{sub}', '{email}', '{name}', '{rid}')"
        for uid, sub, email, name, rid in users
    )
    op.execute(sa.text(
        f"INSERT INTO users (id, oidc_subject, email, display_name, role_id) VALUES {user_values}"
    ))

    # ---------------------------------------------------------------
    # 5. DATA SOURCES
    # ---------------------------------------------------------------
    op.execute(sa.text(
        f"INSERT INTO data_sources (id, name, source_type, base_url, status, records_synced, last_sync_at) VALUES "
        f"('{DS_WORKDAY}', 'Workday', 'procurement', 'http://mock-workday:9001', 'connected', 45, NOW()), "
        f"('{DS_AUDITBOARD}', 'AuditBoard', 'vendor_risk', 'http://mock-auditboard:9002', 'connected', 38, NOW()), "
        f"('{DS_ENTRA}', 'Entra ID', 'identity_analytics', 'http://mock-entra:9003', 'connected', 100, NOW()), "
        f"('{DS_MANUAL}', 'Voluntary Submissions', 'manual', NULL, 'connected', 12, NOW())"
    ))

    # ---------------------------------------------------------------
    # 6. APPLICATIONS (100)
    # ---------------------------------------------------------------
    app_rows = []
    for (name, vendor, category, app_type, status, annual_cost, cpl,
         total_lic, active, dept, ds, risk, compliance, contract_end) in APPS:
        app_id = APP_IDS[name]
        adoption = round((active / total_lic) * 100, 1) if total_lic > 0 else 0
        risk_sql = f"{risk}" if risk is not None else "NULL"
        compliance_sql = f"'{compliance}'" if compliance is not None else "NULL"
        contract_sql = f"'{contract_end}'" if contract_end is not None else "NULL"
        # Escape single quotes in names/vendors
        name_esc = name.replace("'", "''")
        vendor_esc = vendor.replace("'", "''")
        app_rows.append(
            f"('{app_id}', '{name_esc}', '{vendor_esc}', '{category}', '{app_type}', "
            f"'{status}', {annual_cost}, {cpl}, {total_lic}, {active}, {adoption}, "
            f"'{dept}', '{ds}', {risk_sql}, {compliance_sql}, {contract_sql}, NULL)"
        )

    # Insert in batches to avoid overly long SQL statements
    batch_size = 25
    for i in range(0, len(app_rows), batch_size):
        batch = ", ".join(app_rows[i:i + batch_size])
        op.execute(sa.text(
            f"INSERT INTO applications (id, name, vendor, category, app_type, "
            f"status, annual_cost, cost_per_license, total_licenses, active_users, "
            f"adoption_rate, department, data_source, risk_score, compliance_status, "
            f"contract_end, owner_id) VALUES {batch}"
        ))

    # ---------------------------------------------------------------
    # 7. RECOMMENDATIONS (~60)
    # ---------------------------------------------------------------
    rec_rows = []
    for (app_name, rec_type, confidence, reasoning, savings, alt, status) in RECOMMENDATIONS:
        rec_id = REC_IDS[f"{app_name}-{rec_type}"]
        app_id = APP_IDS[app_name]
        savings_sql = f"{savings}" if savings is not None else "NULL"
        alt_sql = f"'{alt}'" if alt is not None else "NULL"
        reasoning_esc = reasoning.replace("'", "''")
        alt_esc = alt_sql.replace("'", "''") if alt else "NULL"
        # Re-do alt escaping properly
        if alt is not None:
            alt_esc = f"'{alt.replace(chr(39), chr(39)+chr(39))}'"
        else:
            alt_esc = "NULL"
        rec_rows.append(
            f"('{rec_id}', '{app_id}', '{rec_type}', {confidence}, '{reasoning_esc}', "
            f"{savings_sql}, {alt_esc}, '{status}')"
        )

    batch_size = 20
    for i in range(0, len(rec_rows), batch_size):
        batch = ", ".join(rec_rows[i:i + batch_size])
        op.execute(sa.text(
            f"INSERT INTO recommendations (id, application_id, recommendation_type, "
            f"confidence_score, reasoning, cost_savings_estimate, alternative_app, status) "
            f"VALUES {batch}"
        ))

    # ---------------------------------------------------------------
    # 8. DECISIONS (~15)
    # ---------------------------------------------------------------
    dec_rows = []
    for idx, (app_name, rec_type, dec_type, justification, submitted_by,
              status, reviewer, cost_impact) in enumerate(DECISIONS):
        dec_id = _uuid(f"dec-{app_name.lower().replace(' ', '-')}-{idx}")
        app_id = APP_IDS[app_name]
        rec_key = f"{app_name}-{rec_type}"
        rec_id = REC_IDS.get(rec_key)
        rec_id_sql = f"'{rec_id}'" if rec_id else "NULL"
        reviewer_sql = f"'{reviewer}'" if reviewer else "NULL"
        reviewed_at_sql = "NOW()" if reviewer else "NULL"
        justification_esc = justification.replace("'", "''")
        cost_sql = f"{cost_impact}" if cost_impact else "NULL"
        dec_rows.append(
            f"('{dec_id}', '{app_id}', {rec_id_sql}, '{dec_type}', "
            f"'{justification_esc}', '{submitted_by}', '{status}', "
            f"{reviewer_sql}, {reviewed_at_sql}, {cost_sql})"
        )

    dec_values = ", ".join(dec_rows)
    op.execute(sa.text(
        f"INSERT INTO decisions (id, application_id, recommendation_id, decision_type, "
        f"justification, submitted_by, status, reviewer_id, reviewed_at, cost_impact) "
        f"VALUES {dec_values}"
    ))


# ===================================================================
# downgrade
# ===================================================================
def downgrade() -> None:
    # Delete in reverse dependency order
    op.execute(sa.text("DELETE FROM decisions"))
    op.execute(sa.text("DELETE FROM recommendations"))
    op.execute(sa.text("DELETE FROM applications"))
    op.execute(sa.text("DELETE FROM data_sources"))
    op.execute(sa.text("DELETE FROM users"))
    op.execute(sa.text("DELETE FROM role_permissions"))
    op.execute(sa.text("DELETE FROM permissions"))
    op.execute(sa.text("DELETE FROM roles"))
