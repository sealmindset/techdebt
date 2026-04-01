"""Seed Tailspend data source, applications, and recommendations

Revision ID: 006
Revises: 005
Create Date: 2025-01-01 00:00:00.000000

Adds Tailspend Analyzer as a data source with ~18 vendor applications
sourced from spend analytics data, plus rationalization recommendations.
"""
from typing import Sequence, Union

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# Deterministic UUID namespace (same as 005_seed_data.py)
# ---------------------------------------------------------------------------
NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _uuid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# DATA SOURCE
# ---------------------------------------------------------------------------
DS_TAILSPEND = _uuid("ds-tailspend")

# ---------------------------------------------------------------------------
# TAILSPEND APPLICATIONS (~18)
# ---------------------------------------------------------------------------
# (name, vendor, category, app_type, status, annual_cost, cost_per_license,
#  total_licenses, active_users, department, data_source, risk_score,
#  compliance_status, contract_end)
APPS = [
    # ---- Group B: New SaaS vendors ----
    ("DocuSign eSignature", "DocuSign", "Productivity", "saas", "active", 84000, 25, 280, 250, "Legal", "tailspend", 8, "compliant", "2027-01-15"),
    ("Okta Identity Cloud", "Okta", "Security", "saas", "active", 192000, 8, 5000, 4800, "Security", "tailspend", 5, "compliant", "2027-03-31"),
    ("ServiceNow ITSM", "ServiceNow", "IT Operations", "saas", "active", 420000, 70, 500, 460, "IT", "tailspend", 6, "compliant", "2026-12-31"),
    ("Adobe Creative Cloud", "Adobe", "Marketing", "saas", "active", 156000, 55, 250, 220, "Marketing", "tailspend", 7, "compliant", "2026-09-30"),
    ("HubSpot Marketing Hub", "HubSpot", "Marketing", "saas", "active", 108000, 45, 200, 180, "Marketing", "tailspend", 10, "compliant", "2026-11-30"),
    ("Gong Revenue Intelligence", "Gong", "Sales", "saas", "active", 132000, 110, 100, 85, "Sales", "tailspend", 12, "compliant", "2026-08-15"),
    ("Shopify Plus", "Shopify", "E-Commerce", "saas", "active", 240000, 0, 50, 45, "E-Commerce", "tailspend", 8, "compliant", "2027-06-30"),
    ("Samsara Fleet", "Samsara", "Operations", "saas", "active", 96000, 40, 200, 180, "Operations", "tailspend", 15, "compliant", "2026-10-15"),
    ("ThoughtSpot Analytics", "ThoughtSpot", "Analytics", "saas", "under_review", 72000, 60, 100, 35, "Engineering", "tailspend", 40, "pending_review", "2025-11-30"),
    ("Anaplan FP&A", "Anaplan", "Finance", "saas", "active", 180000, 150, 100, 90, "Finance", "tailspend", 9, "compliant", "2027-02-28"),
    ("Zuora Billing", "Zuora", "Finance", "saas", "active", 96000, 80, 100, 90, "Finance", "tailspend", 10, "compliant", "2026-12-15"),

    # ---- Group C: Tail-spend / rationalization candidates ----
    ("Calendly", "Calendly", "Productivity", "saas", "under_review", 12000, 8, 125, 40, "Sales", "tailspend", 25, "pending_review", "2025-12-31"),
    ("Grammarly Business", "Grammarly", "Productivity", "saas", "under_review", 18000, 12, 125, 30, "Marketing", "tailspend", 30, "pending_review", "2025-10-15"),
    ("Canva Enterprise", "Canva", "Marketing", "saas", "under_review", 24000, 13, 150, 55, "Marketing", "tailspend", 28, "pending_review", "2025-09-30"),
    ("SurveyMonkey Enterprise", "SurveyMonkey", "Analytics", "saas", "under_review", 9600, 16, 50, 18, "Marketing", "tailspend", 35, "pending_review", "2025-08-31"),
    ("Otter.ai Business", "Otter.ai", "Productivity", "saas", "active", 7200, 12, 50, 42, "All Departments", "tailspend", 18, "compliant", "2026-06-30"),
    ("Box Enterprise", "Box", "Collaboration", "saas", "under_review", 48000, 16, 250, 60, "Engineering", "tailspend", 42, "pending_review", "2025-07-31"),
    ("Vimeo Enterprise", "Vimeo", "Communication", "saas", "under_review", 15000, 25, 50, 15, "Marketing", "tailspend", 45, "pending_review", "2025-06-30"),
]

# Compute app IDs deterministically
APP_IDS = {app[0]: _uuid(f"app-{app[0].lower().replace(' ', '-')}") for app in APPS}

# ---------------------------------------------------------------------------
# RECOMMENDATIONS for Tailspend apps
# ---------------------------------------------------------------------------
# (app_name, recommendation_type, confidence, reasoning, cost_savings, alternative, status)
RECOMMENDATIONS = [
    # KEEP
    ("Okta Identity Cloud", "keep", 94, "96% adoption as sole identity provider. Critical security infrastructure with no viable alternative at this scale. Tailspend confirms competitive pricing.", None, None, "pending"),
    ("ServiceNow ITSM", "keep", 92, "92% adoption across IT operations. Core ITSM platform deeply integrated with change management and CMDB. Tailspend spend data confirms stable year-over-year costs.", None, None, "pending"),
    ("Shopify Plus", "keep", 90, "90% platform utilization for DTC e-commerce. Revenue-generating system processing significant online sales. Tailspend shows spend aligned with transaction volume growth.", None, None, "pending"),
    ("Adobe Creative Cloud", "keep", 88, "88% adoption among marketing and brand teams. Industry-standard creative tools with no cost-effective replacement. Tailspend capability data confirms strategic fit.", None, None, "pending"),

    # CUT
    ("Calendly", "cut", 85, "32% adoption (40 of 125 users). Microsoft Bookings in M365 provides equivalent scheduling. Tailspend flags as redundant with existing enterprise license.", 12000, None, "pending"),
    ("SurveyMonkey Enterprise", "cut", 82, "36% adoption (18 of 50 users). Microsoft Forms available at no additional cost through M365. Tailspend spend analysis shows declining usage trend.", 9600, None, "pending"),
    ("Vimeo Enterprise", "cut", 80, "30% adoption (15 of 50 users). Video hosting needs covered by Zoom recordings and Loom. Tailspend identifies as lowest-value communication tool.", 15000, None, "pending"),

    # REPLACE
    ("Box Enterprise", "replace", 78, "24% adoption (60 of 250 users). SharePoint/OneDrive is the enterprise file storage standard with 96% M365 adoption. Tailspend contract data shows auto-renewal risk -- cancel before July 2025.", 48000, "SharePoint/OneDrive", "pending"),

    # CONSOLIDATE
    ("Canva Enterprise", "consolidate", 76, "37% adoption. Design capabilities overlap with Adobe Creative Cloud (88% adoption). Tailspend capability analysis confirms functional redundancy. Consolidate non-designer use cases into Adobe Express.", 24000, "Adobe Creative Cloud", "pending"),
    ("Grammarly Business", "consolidate", 74, "24% adoption. Writing assistance now available through M365 Copilot and Editor. Tailspend flags as redundant with existing Microsoft investment.", 18000, "Microsoft 365 (Copilot/Editor)", "pending"),
    ("ThoughtSpot Analytics", "replace", 77, "35% adoption (35 of 100 users). Tableau (84% adoption) and Power BI (85% adoption) cover all analytics needs. Tailspend spend data shows flat growth indicating stalled adoption.", 72000, "Tableau + Power BI", "pending"),
]

REC_IDS = {f"{r[0]}-{r[1]}": _uuid(f"rec-{r[0].lower().replace(' ', '-')}-{r[1]}") for r in RECOMMENDATIONS}


# ===================================================================
# upgrade
# ===================================================================
def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. DATA SOURCE
    # ---------------------------------------------------------------
    op.execute(sa.text(
        f"INSERT INTO data_sources (id, name, source_type, base_url, status, records_synced, last_sync_at) VALUES "
        f"('{DS_TAILSPEND}', 'Tailspend', 'spend_analytics', 'http://mock-tailspend:9004', 'connected', 18, NOW())"
    ))

    # ---------------------------------------------------------------
    # 2. APPLICATIONS (18)
    # ---------------------------------------------------------------
    app_rows = []
    for (name, vendor, category, app_type, status, annual_cost, cpl,
         total_lic, active, dept, ds, risk, compliance, contract_end) in APPS:
        app_id = APP_IDS[name]
        adoption = round((active / total_lic) * 100, 1) if total_lic > 0 else 0
        risk_sql = f"{risk}" if risk is not None else "NULL"
        compliance_sql = f"'{compliance}'" if compliance is not None else "NULL"
        contract_sql = f"'{contract_end}'" if contract_end is not None else "NULL"
        name_esc = name.replace("'", "''")
        vendor_esc = vendor.replace("'", "''")
        app_rows.append(
            f"('{app_id}', '{name_esc}', '{vendor_esc}', '{category}', '{app_type}', "
            f"'{status}', {annual_cost}, {cpl}, {total_lic}, {active}, {adoption}, "
            f"'{dept}', '{ds}', {risk_sql}, {compliance_sql}, {contract_sql}, NULL)"
        )

    batch = ", ".join(app_rows)
    op.execute(sa.text(
        f"INSERT INTO applications (id, name, vendor, category, app_type, "
        f"status, annual_cost, cost_per_license, total_licenses, active_users, "
        f"adoption_rate, department, data_source, risk_score, compliance_status, "
        f"contract_end, owner_id) VALUES {batch}"
    ))

    # ---------------------------------------------------------------
    # 3. RECOMMENDATIONS (11)
    # ---------------------------------------------------------------
    rec_rows = []
    for (app_name, rec_type, confidence, reasoning, savings, alt, status) in RECOMMENDATIONS:
        rec_id = REC_IDS[f"{app_name}-{rec_type}"]
        app_id = APP_IDS[app_name]
        savings_sql = f"{savings}" if savings is not None else "NULL"
        reasoning_esc = reasoning.replace("'", "''")
        if alt is not None:
            alt_esc = f"'{alt.replace(chr(39), chr(39)+chr(39))}'"
        else:
            alt_esc = "NULL"
        rec_rows.append(
            f"('{rec_id}', '{app_id}', '{rec_type}', {confidence}, '{reasoning_esc}', "
            f"{savings_sql}, {alt_esc}, '{status}')"
        )

    rec_batch = ", ".join(rec_rows)
    op.execute(sa.text(
        f"INSERT INTO recommendations (id, application_id, recommendation_type, "
        f"confidence_score, reasoning, cost_savings_estimate, alternative_app, status) "
        f"VALUES {rec_batch}"
    ))


# ===================================================================
# downgrade
# ===================================================================
def downgrade() -> None:
    # Delete recommendations for tailspend apps
    app_ids = [f"'{aid}'" for aid in APP_IDS.values()]
    app_id_list = ", ".join(app_ids)
    op.execute(sa.text(
        f"DELETE FROM recommendations WHERE application_id IN ({app_id_list})"
    ))
    # Delete tailspend applications
    op.execute(sa.text(
        f"DELETE FROM applications WHERE data_source = 'tailspend'"
    ))
    # Delete the data source
    op.execute(sa.text(
        f"DELETE FROM data_sources WHERE id = '{DS_TAILSPEND}'"
    ))
