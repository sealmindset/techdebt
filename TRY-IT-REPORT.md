# TechDebt -- Try-It Report
> Tested: 2026-03-31
> Status: All Passing

## Summary

Your app was tested automatically. Here's what happened:

| What Was Tested | Result |
|----------------|--------|
| App starts up (7 services) | PASS |
| Login works (all 5 roles) | PASS |
| All pages load (12 pages) | PASS |
| Permissions work correctly | PASS |
| API is responding (14 endpoints) | PASS |
| Mock services return data | PASS |
| AI Prompt Management (8 prompts) | PASS |
| Logout works | PASS |

## Login Testing

Each type of user was tested:

| User | Email | Role | Login | Dashboard | API Access | Admin Access |
|------|-------|------|-------|-----------|------------|--------------|
| Admin User | admin@techdebt.local | Super Admin | PASS | PASS | Full | Full |
| IT Admin | itadmin@techdebt.local | Admin | PASS | PASS | Full | Full |
| Finance Reviewer | finance@techdebt.local | Finance Reviewer | PASS | PASS | Domain only | Blocked (403) |
| Department Head | depthead@techdebt.local | Department Head | PASS | PASS | Domain only | Blocked (403) |
| Viewer User | viewer@techdebt.local | Viewer | PASS | PASS | Domain only | Blocked (403) |

## Pages Tested

| Page | Super Admin | Admin | Finance / DeptHead / Viewer |
|------|-------------|-------|---------------------------|
| Dashboard | PASS | PASS | PASS |
| Applications | PASS | PASS | PASS |
| Recommendations | PASS | PASS | PASS |
| Decisions | PASS | PASS | PASS |
| Data Sources | PASS | PASS | PASS |
| Submissions | PASS | PASS | PASS |
| Admin - Users | PASS | PASS | N/A (no access) |
| Admin - Roles | PASS | PASS | N/A (no access) |
| Admin - Settings | PASS | PASS | N/A (no access) |
| Admin - Activity Logs | PASS | PASS | N/A (no access) |
| Admin - AI Instructions | PASS | PASS (read) | N/A (no access) |
| AI Instructions - Detail | PASS | PASS (read) | N/A (no access) |

## API Endpoints Tested

| Endpoint | Status | Data |
|----------|--------|------|
| GET /api/dashboard | 200 | 118 apps, $23.16M spend, 61.3% adoption, $163K savings, 10 opportunities, 10 decisions |
| GET /api/applications | 200 | 118 applications across 15 categories |
| GET /api/recommendations | 200 | 60 recommendations |
| GET /api/decisions | 200 | 15 decisions |
| GET /api/data-sources | 200 | 4 data sources |
| GET /api/submissions | 200 | 0 (empty -- voluntary submissions) |
| GET /api/users | 200 | User management |
| GET /api/roles | 200 | Role management |
| GET /api/admin/settings | 200 | App settings |
| GET /api/admin/logs/stats | 200 | Activity log stats |
| GET /api/admin/prompts | 200 | 8 AI prompts (rationalization, cost analysis, risk, analytics, reporting, finance, intake) |
| GET /api/admin/prompts/stats | 200 | Prompt statistics (8 total, 7 categories) |
| GET /api/admin/prompts/{id} | 200 | Full prompt detail with versions, tags, usages, test cases |
| POST /api/auth/logout | 200 | Cookie cleared |

## AI Prompt Management

8 prompts seeded covering the full rationalization pipeline:

| Prompt | Category | Model | Tags | Test Cases |
|--------|----------|-------|------|------------|
| App Rationalization Engine | rationalization | claude-sonnet-4-20250514 | rationalization, decision-support, core | 3 |
| Cost Savings Analyzer | finance | claude-sonnet-4-20250514 | cost-optimization, savings, financial-analysis | 3 |
| Consolidation Finder | rationalization | claude-sonnet-4-20250514 | consolidation, portfolio, deduplication | 3 |
| Vendor Risk Assessor | risk | claude-sonnet-4-20250514 | risk-assessment, vendor, compliance | 3 |
| Usage Trend Analyzer | analytics | claude-sonnet-4-20250514 | usage-analytics, trends, adoption | 3 |
| Decision Summary Generator | reporting | claude-sonnet-4-20250514 | reporting, executive-summary, decisions | 3 |
| Procurement Contract Analyzer | finance | claude-sonnet-4-20250514 | procurement, contracts, renewal | 3 |
| Submission Classifier | intake | claude-haiku-4-5-20251001 | classification, intake, triage | 3 |

Each prompt includes: version history (v1), usage locations, tags, test cases, and audit trail.

## Mock Services

| Service | Port | Status | Data |
|---------|------|--------|------|
| mock-oidc | 10090 | Healthy | 5 test users |
| mock-workday | 9101 | Healthy | 32 procurement contracts |
| mock-auditboard | 9002 | Healthy | 24 vendors with risk assessments |
| mock-entra | 9003 | Healthy | 40 apps with sign-in analytics |

## How to Access Your App

- **Open your browser to:** http://localhost:3100
- **To log in:** Click "Sign In", then pick a user from the login screen:
  - **Admin User** -- Full access to everything, including admin features and AI Instructions
  - **IT Admin** -- Can manage apps, data sources, and review decisions
  - **Finance Reviewer** -- Can review costs and approve/reject financial decisions
  - **Department Head** -- Can submit recommendations for their department's apps
  - **Viewer User** -- Read-only access to dashboards and app details

## What to Do Next
- Explore your app in the browser (see instructions above)
- Check out the **AI Instructions** page (Admin menu) to see all 8 prompts powering the rationalization engine
- Click into any prompt to see its version history, where it's used, and test cases
- If something doesn't look right, tell me and I'll fix it
- When you're happy with how it works, type **/ship-it** to deploy
- To make changes or add features, type **/resume-it**
- To save progress and shut down, type **/wrap-it**
