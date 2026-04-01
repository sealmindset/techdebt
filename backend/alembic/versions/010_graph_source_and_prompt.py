"""Add Microsoft Graph data source and Graph Intelligence AI prompt

Revision ID: 010
Revises: 009
Create Date: 2025-01-01 00:00:00.000000

Seeds the Microsoft Graph API as a data source and adds the
Graph Intelligence Analyzer prompt to AI Instructions.
"""
from typing import Sequence, Union

import uuid
import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _uuid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# IDs
DS_GRAPH = _uuid("ds-microsoft-graph")
PROMPT_ID = _uuid("prompt-graph-intelligence")
VERSION_ID = _uuid("prompt-graph-intelligence-v1")
USER_ADMIN = _uuid("user-mock-admin")


def upgrade() -> None:
    # ---------------------------------------------------------------
    # 1. Data Source: Microsoft Graph API
    # ---------------------------------------------------------------
    op.execute(sa.text(
        f"INSERT INTO data_sources "
        f"(id, name, source_type, base_url, status, records_synced, "
        f" last_sync_at, is_primary, auth_method) VALUES "
        f"('{DS_GRAPH}', 'Microsoft Graph', 'graph_discovery', "
        f" 'http://mock-graph:9005', 'connected', 115, NOW(), true, "
        f" 'oauth2_client_credentials')"
    ))

    # ---------------------------------------------------------------
    # 2. AI Prompt: Graph Intelligence Analyzer
    # ---------------------------------------------------------------
    system_message = (
        "You are a Microsoft Graph Intelligence Analyst specializing in SaaS "
        "rationalization. You analyze data from Microsoft Graph API -- including "
        "service principal inventories, sign-in logs, license utilization, and "
        "M365 usage reports -- to provide actionable intelligence for IT decision "
        "makers.\\n\\n"
        "Your analysis must be:\\n"
        "- Data-driven: cite specific numbers from the Graph data\\n"
        "- Actionable: every finding should have a clear next step\\n"
        "- Prioritized: rank findings by potential cost impact and risk\\n"
        "- Contextual: explain why each finding matters for rationalization"
    )

    content = (
        "Analyze the following Microsoft Graph intelligence data and produce "
        "a comprehensive SaaS rationalization report.\\n\\n"
        "## Graph Intelligence Data\\n"
        "```json\\n{{graph_intelligence_json}}\\n```\\n\\n"
        "## Existing TechDebt Application Inventory\\n"
        "```json\\n{{existing_apps_json}}\\n```\\n\\n"
        "## Analysis Required\\n\\n"
        "### 1. Shadow IT Discovery\\n"
        "Compare service principals against the existing inventory. For each "
        "unrecognized app:\\n"
        "- Identify the app name, publisher, and category\\n"
        "- Estimate usage level from sign-in data\\n"
        "- Assess risk level (data sensitivity, compliance gaps, security posture)\\n"
        "- Recommend: ONBOARD (add to inventory), BLOCK (security risk), or MONITOR\\n\\n"
        "### 2. Usage & Adoption Intelligence\\n"
        "For apps in both Graph and the inventory:\\n"
        "- Compare Graph sign-in data against reported adoption rates\\n"
        "- Flag discrepancies (e.g., app reports 90% adoption but Graph shows 20% active sign-ins)\\n"
        "- Identify apps with declining sign-in trends (potential CUT candidates)\\n"
        "- Highlight apps with increasing usage (validate KEEP recommendations)\\n\\n"
        "### 3. License Optimization\\n"
        "Analyze subscribedSkus data:\\n"
        "- Calculate total license waste (assigned - active) per SKU\\n"
        "- Estimate annual cost savings from right-sizing licenses\\n"
        "- Recommend specific license tier changes (e.g., E5 -> E3 for low-usage users)\\n"
        "- Identify users who could be moved to cheaper license tiers\\n\\n"
        "### 4. M365 Suite Rationalization\\n"
        "Cross-reference M365 product usage with third-party alternatives:\\n"
        "- If Teams adoption is 98% but Slack is also active, quantify the overlap\\n"
        "- If SharePoint adoption is low, assess if external tools (Notion, Confluence) are substitutes\\n"
        "- Calculate the cost of maintaining parallel tools vs. standardizing\\n\\n"
        "### 5. Risk & Compliance\\n"
        "From sign-in risk data:\\n"
        "- Flag apps with elevated risk sign-ins\\n"
        "- Identify apps not protected by conditional access\\n"
        "- Note disabled service principals that still have sign-in attempts\\n\\n"
        "## Output Format\\n"
        "```json\\n"
        "{\\n"
        "  \\\"executive_summary\\\": \\\"2-3 sentence overview\\\",\\n"
        "  \\\"shadow_it_findings\\\": [\\n"
        "    {\\n"
        "      \\\"app_name\\\": \\\"string\\\",\\n"
        "      \\\"publisher\\\": \\\"string\\\",\\n"
        "      \\\"category\\\": \\\"string\\\",\\n"
        "      \\\"estimated_users\\\": 0,\\n"
        "      \\\"risk_level\\\": \\\"low|medium|high|critical\\\",\\n"
        "      \\\"recommendation\\\": \\\"ONBOARD|BLOCK|MONITOR\\\",\\n"
        "      \\\"reasoning\\\": \\\"string\\\"\\n"
        "    }\\n"
        "  ],\\n"
        "  \\\"usage_insights\\\": [\\n"
        "    {\\n"
        "      \\\"app_name\\\": \\\"string\\\",\\n"
        "      \\\"reported_adoption\\\": 0.0,\\n"
        "      \\\"graph_adoption\\\": 0.0,\\n"
        "      \\\"discrepancy\\\": \\\"string\\\",\\n"
        "      \\\"trend\\\": \\\"increasing|stable|declining\\\",\\n"
        "      \\\"impact_on_recommendation\\\": \\\"string\\\"\\n"
        "    }\\n"
        "  ],\\n"
        "  \\\"license_savings\\\": {\\n"
        "    \\\"total_wasted_licenses\\\": 0,\\n"
        "    \\\"estimated_annual_savings\\\": 0.0,\\n"
        "    \\\"recommendations\\\": [\\n"
        "      {\\n"
        "        \\\"sku\\\": \\\"string\\\",\\n"
        "        \\\"current_assigned\\\": 0,\\n"
        "        \\\"recommended_assigned\\\": 0,\\n"
        "        \\\"annual_savings\\\": 0.0,\\n"
        "        \\\"action\\\": \\\"string\\\"\\n"
        "      }\\n"
        "    ]\\n"
        "  },\\n"
        "  \\\"m365_overlap\\\": [\\n"
        "    {\\n"
        "      \\\"m365_product\\\": \\\"string\\\",\\n"
        "      \\\"competing_app\\\": \\\"string\\\",\\n"
        "      \\\"overlap_users\\\": 0,\\n"
        "      \\\"consolidation_savings\\\": 0.0,\\n"
        "      \\\"recommendation\\\": \\\"string\\\"\\n"
        "    }\\n"
        "  ],\\n"
        "  \\\"risk_alerts\\\": [\\n"
        "    {\\n"
        "      \\\"app_name\\\": \\\"string\\\",\\n"
        "      \\\"risk_type\\\": \\\"string\\\",\\n"
        "      \\\"severity\\\": \\\"low|medium|high|critical\\\",\\n"
        "      \\\"action_required\\\": \\\"string\\\"\\n"
        "    }\\n"
        "  ],\\n"
        "  \\\"total_potential_savings\\\": 0.0,\\n"
        "  \\\"priority_actions\\\": [\\\"top 5 actions ranked by impact\\\"]\\n"
        "}\\n"
        "```"
    )

    parameters = json.dumps({
        "temperature": 0.15,
        "max_tokens": 4096,
        "top_p": 0.95,
    })

    # Escape single quotes for SQL
    system_message_sql = system_message.replace("'", "''")
    content_sql = content.replace("'", "''")

    # Insert prompt
    op.execute(sa.text(
        f"INSERT INTO managed_prompts "
        f"(id, slug, name, description, category, provider, model, "
        f" current_version, is_active, source_file, created_by) VALUES "
        f"('{PROMPT_ID}', 'graph-intelligence', "
        f" 'Graph Intelligence Analyzer', "
        f" 'Analyzes Microsoft Graph API data (service principals, sign-in logs, "
        f"license SKUs, M365 usage) to discover shadow IT, identify usage anomalies, "
        f"optimize licenses, and produce actionable rationalization intelligence.', "
        f" 'intelligence', 'anthropic', 'claude-sonnet-4-20250514', "
        f" 1, true, 'backend/app/services/graph_analyzer.py', "
        f" '{USER_ADMIN}')"
    ))

    # Insert version
    op.execute(sa.text(
        f"INSERT INTO prompt_versions "
        f"(id, prompt_id, version, content, system_message, parameters, "
        f" change_summary, created_by) VALUES "
        f"('{VERSION_ID}', '{PROMPT_ID}', 1, "
        f" '{content_sql}', '{system_message_sql}', "
        f" '{parameters}'::jsonb, "
        f" 'Initial version: Graph Intelligence Analyzer for SaaS rationalization', "
        f" '{USER_ADMIN}')"
    ))

    # Insert tags
    tags = [
        ("graph", PROMPT_ID),
        ("microsoft", PROMPT_ID),
        ("shadow-it", PROMPT_ID),
        ("license-optimization", PROMPT_ID),
        ("intelligence", PROMPT_ID),
        ("discovery", PROMPT_ID),
    ]
    tag_values = ", ".join(
        f"('{_uuid('tag-' + t + '-' + pid)}', '{pid}', '{t}')"
        for t, pid in tags
    )
    op.execute(sa.text(
        f"INSERT INTO prompt_tags (id, prompt_id, tag) VALUES {tag_values}"
    ))

    # Insert usages
    usages = [
        (_uuid("usage-graph-service"), PROMPT_ID, "service",
         "backend/app/services/graph_analyzer.py",
         "Called after Graph API sync to analyze discovered data", True),
        (_uuid("usage-graph-api"), PROMPT_ID, "api",
         "/api/data-sources/{id}/analyze",
         "Triggered when user requests AI analysis of Graph sync results", False),
        (_uuid("usage-graph-page"), PROMPT_ID, "page",
         "frontend/app/(auth)/data-sources/page.tsx",
         "Powers the Graph Intelligence dashboard panel", False),
    ]
    usage_values = ", ".join(
        f"('{uid}', '{pid}', '{utype}', '{loc}', '{desc}', {str(primary).lower()})"
        for uid, pid, utype, loc, desc, primary in usages
    )
    op.execute(sa.text(
        f"INSERT INTO prompt_usages "
        f"(id, prompt_id, usage_type, location, description, is_primary) "
        f"VALUES {usage_values}"
    ))

    # Insert test cases
    test_cases = [
        {
            "id": _uuid("test-graph-shadow-it"),
            "name": "Should flag shadow IT apps with ONBOARD/BLOCK recommendations",
            "input_data": json.dumps({
                "graph_intelligence_json": json.dumps({
                    "shadowItDiscovery": [
                        {"appName": "ChatGPT Enterprise", "publisher": "OpenAI",
                         "category": "AI & ML", "signInCount30d": 280,
                         "uniqueUsers30d": 350, "notes": "No IT approval"},
                        {"appName": "DocuSign", "publisher": "DocuSign",
                         "category": "Finance", "signInCount30d": 25,
                         "uniqueUsers30d": 80,
                         "notes": "Contract signing without governance"},
                    ]
                }),
                "existing_apps_json": "[]",
            }),
            "expected_output": "ONBOARD for ChatGPT (high usage), BLOCK or ONBOARD with controls for DocuSign (compliance risk)",
            "notes": "Shadow IT discovery should recommend based on usage volume and compliance risk",
        },
        {
            "id": _uuid("test-graph-license-waste"),
            "name": "Should identify license waste and savings opportunities",
            "input_data": json.dumps({
                "graph_intelligence_json": json.dumps({
                    "licenseWaste": {
                        "totalWastedLicenses": 2575,
                        "estimatedAnnualWaste": 1081500,
                        "topWaste": [
                            {"sku": "Microsoft 365 E3", "assigned": 1200,
                             "available": 2000, "unused": 800},
                            {"sku": "Visio Plan 2", "assigned": 45,
                             "available": 200, "unused": 155},
                        ],
                    }
                }),
                "existing_apps_json": "[]",
            }),
            "expected_output": "Right-size M365 E3 licenses from 2000 to ~1300, reduce Visio from 200 to ~60",
            "notes": "License optimization should recommend specific reduction targets with cost savings",
        },
    ]

    for tc in test_cases:
        input_sql = tc["input_data"].replace("'", "''")
        expected_sql = tc["expected_output"].replace("'", "''")
        notes_sql = tc["notes"].replace("'", "''")
        op.execute(sa.text(
            f"INSERT INTO prompt_test_cases "
            f"(id, prompt_id, name, input_data, expected_output, notes, created_by) "
            f"VALUES ('{tc['id']}', '{PROMPT_ID}', '{tc['name']}', "
            f" '{input_sql}'::jsonb, '{expected_sql}', '{notes_sql}', "
            f" '{USER_ADMIN}')"
        ))

    # Audit log entry
    op.execute(sa.text(
        f"INSERT INTO prompt_audit_log "
        f"(id, action, prompt_id, prompt_slug, version, user_id, user_email) "
        f"VALUES ('{_uuid('audit-graph-prompt-create')}', 'prompt_created', "
        f" '{PROMPT_ID}', 'graph-intelligence', 1, "
        f" '{USER_ADMIN}', 'admin@techdebt.local')"
    ))


def downgrade() -> None:
    op.execute(sa.text(
        f"DELETE FROM prompt_audit_log WHERE prompt_id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM prompt_test_cases WHERE prompt_id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM prompt_usages WHERE prompt_id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM prompt_tags WHERE prompt_id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM prompt_versions WHERE prompt_id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM managed_prompts WHERE id = '{PROMPT_ID}'"
    ))
    op.execute(sa.text(
        f"DELETE FROM data_sources WHERE id = '{DS_GRAPH}'"
    ))
