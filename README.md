# TechDebt

**SaaS Rationalization Platform** -- Know what software your organization pays for, who actually uses it, and what to do about it.

---

## What Is This?

TechDebt helps IT, Finance, and leadership teams make confident decisions about their software portfolio. It pulls data from the systems you already use -- procurement, identity, risk, spend analytics, and Microsoft Graph -- and brings it all together in one place.

Instead of spreadsheets and guesswork, you get a clear picture:

- **What do we pay for?** Contracts, licenses, and costs from Workday
- **Who actually uses it?** Sign-in data and adoption rates from Entra ID and Microsoft Graph
- **Is it risky?** Vendor risk and compliance scores from AuditBoard
- **Where are we wasting money?** Spend analytics from Tailspend
- **What's hiding in the shadows?** Shadow IT discovery via Microsoft Graph service principals

Then AI analyzes the data and recommends what to **keep**, **cut**, **replace**, or **consolidate** -- with evidence and cost impact for each decision.

## Who Is This For?

| Role | What You Do In TechDebt |
|------|------------------------|
| **IT Asset Management** | Manage the full app portfolio, connect data sources, review AI recommendations |
| **Finance** | Review cost data, approve or reject spending decisions |
| **Department Heads** | Submit recommendations for apps in your department with justification |
| **Leadership / Viewers** | View dashboards, track decisions, monitor portfolio health |

## What You Can Do

- **Dashboard** -- See total apps under review, total spend, average adoption rate, and AI recommendation breakdown at a glance
- **Application Portfolio** -- Browse 100+ applications with search, filtering by category/status/recommendation, and drill-down detail pages showing usage stats, cost per user, and adoption trends
- **AI Recommendations** -- Review AI-generated keep/cut/replace/consolidate recommendations backed by data from all connected sources
- **Decision Workflow** -- Department heads submit recommendations with justification; IT and Finance review and approve
- **Data Sources** -- Connect and manage integrations (Workday, AuditBoard, Entra ID, Tailspend, Microsoft Graph), monitor sync status, test connections, add new sources from a built-in catalog
- **Microsoft Graph Intelligence** -- Discover shadow IT apps, analyze license waste, compare M365 adoption vs. third-party overlap, and flag security risks
- **AI Instructions** -- Manage and version the AI prompts that power analysis (Graph Intelligence Analyzer, Cost Savings, Consolidation Finder, Vendor Risk Assessment, and more)
- **Voluntary Submissions** -- Employees can report apps they use that IT might not know about
- **Admin** -- Manage users, roles, permissions, application settings, and activity logs

---

## Prerequisites

You need three things installed on your machine:

| Tool | What It Does | How to Install |
|------|-------------|----------------|
| **Git** | Version control | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Docker Desktop** | Runs the app and all its services | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Node.js 18+** | Only needed if you want to run the frontend outside Docker | [nodejs.org](https://nodejs.org/) (optional) |

**Docker Desktop** is the only real requirement beyond Git. Everything else -- the database, the backend, the frontend, the mock services -- all runs inside Docker containers.

### Verify Your Setup

```bash
git --version    # Should show 2.x or higher
docker --version # Should show 24.x or higher
docker compose version # Should show 2.x or higher
```

---

## Quick Start

Get the app running in under 5 minutes.

### 1. Clone the Repository

```bash
git clone https://github.com/SleepNumberInc/techdebt.git
cd techdebt
```

### 2. Create Your Environment File

```bash
cp .env.example .env
```

Then generate a JWT secret and add it to `.env`:

```bash
# macOS / Linux
openssl rand -hex 32
```

Open `.env` in any text editor and paste the generated value after `JWT_SECRET=`.

### 3. Start the App

```bash
docker compose --profile dev up --build -d
```

This builds and starts 8 services:
- **Frontend** (Next.js) -- your browser interface
- **Backend** (FastAPI) -- the API server
- **Database** (PostgreSQL) -- stores all application data
- **Mock OIDC** -- simulates corporate single sign-on
- **Mock Workday** -- simulates procurement data
- **Mock AuditBoard** -- simulates vendor risk data
- **Mock Entra ID** -- simulates identity/usage analytics
- **Mock Graph** -- simulates Microsoft Graph API (app discovery, licenses, sign-ins)

The first build takes 2-3 minutes. Subsequent starts take about 15 seconds.

### 4. Seed the Login System

```bash
bash scripts/seed-mock-services.sh
```

This registers test users and configures the login redirect. You only need to run this once (or after recreating containers).

### 5. Open the App

Go to **http://localhost:3100** in your browser.

You'll see a login screen with test users. Pick one to sign in:

| User | Role | What They Can Access |
|------|------|---------------------|
| **Admin User** | Super Admin | Everything -- full admin access |
| **IT Admin** | Admin | App portfolio, data sources, recommendations, decisions |
| **Finance Reviewer** | Finance Reviewer | Cost data, financial decisions |
| **Department Head** | Department Head | Submit recommendations, view dashboards |
| **Viewer User** | Viewer | Read-only access to dashboards and app details |

---

## Architecture

```
Browser
  |
  v
Frontend (Next.js, port 3100)
  |  -- same-origin proxy for API calls
  v
Backend (FastAPI, port 8100)
  |  -- async Python, JWT auth, RBAC middleware
  v
PostgreSQL (port 5500)
  |  -- 10 Alembic migrations, 100+ seeded apps
  |
  +-- Mock Workday (port 9001)      -- procurement contracts
  +-- Mock AuditBoard (port 9002)   -- vendor risk scores
  +-- Mock Entra ID (port 9003)     -- sign-in analytics
  +-- Mock Tailspend (port 9004)    -- spend analytics
  +-- Mock Graph (port 9005)        -- Microsoft Graph API
  +-- Mock OIDC (port 10090)        -- corporate SSO simulation
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL 16 with Alembic migrations |
| Auth | OIDC (Azure AD in production, mock-oidc locally) |
| Authorization | Database-driven RBAC with permission middleware |
| AI | Managed prompt system with versioning, tagging, and test cases |
| Infrastructure | Docker Compose with health checks on all services |

### Authentication Flow

The app uses OpenID Connect (OIDC) for authentication:

1. User clicks "Sign In" and is redirected to the identity provider
2. After authenticating, the provider sends back an authorization code
3. The backend exchanges the code for user identity (server-to-server, never exposed to the browser)
4. The backend looks up the user in the database to get their role and permissions
5. A signed JWT cookie is set -- this is your session

**Key point:** Roles and permissions come from the application database, not from the identity provider. This means you can manage access entirely within TechDebt.

### Data Source Integration

Each data source type owns specific fields on the Application model to prevent conflicts:

| Source Type | Authoritative Fields |
|------------|---------------------|
| Procurement (Workday) | Cost, licenses, contract dates, vendor |
| Identity Analytics (Entra ID) | Active users, adoption rate, last login |
| Vendor Risk (AuditBoard) | Risk score, compliance status |
| Spend Analytics (Tailspend) | Annual cost, cost per license |
| Platform Intelligence (Graph) | Active users, adoption, app name, vendor, category |
| Manual | Any field not owned by another source |

---

## Common Tasks

### Stop the App

```bash
docker compose --profile dev down
```

Your data is preserved in a Docker volume. Next time you start, everything is right where you left it.

### Reset Everything (Fresh Start)

```bash
docker compose --profile dev down -v   # -v removes the database volume
docker compose --profile dev up --build -d
bash scripts/seed-mock-services.sh
```

### View Logs

```bash
# All services
docker compose --profile dev logs -f

# Just the backend
docker compose --profile dev logs -f backend

# Just mock-graph
docker compose --profile dev logs -f mock-graph
```

### Run Backend Tests

```bash
docker compose --profile dev exec backend pytest -v
```

### Check Service Health

```bash
docker compose --profile dev ps
```

All services should show `(healthy)` in the STATUS column.

---

## Project Structure

```
techdebt/
  backend/
    app/
      main.py              # FastAPI application entry point
      models/              # SQLAlchemy models (Application, DataSource, Decision, etc.)
      routers/             # API endpoints (auth, applications, data-sources, etc.)
      schemas/             # Pydantic request/response models
      middleware/           # Auth, permissions, request logging
      services/            # Log service, prompt service, settings service
    alembic/versions/      # Database migrations (001-010)
    tests/                 # pytest unit and integration tests
  frontend/
    app/                   # Next.js App Router pages
      (auth)/              # Authenticated pages (dashboard, applications, etc.)
      login/               # Login page
    components/            # Reusable UI components (DataTable, sidebar, modals, etc.)
    lib/                   # API client, auth context, types
  mock-services/
    mock-oidc/             # Corporate SSO simulator
    mock-workday/          # Procurement data (contracts, licenses)
    mock-auditboard/       # Vendor risk and compliance scores
    mock-entra/            # Identity analytics (sign-ins, usage)
    mock-tailspend/        # Spend analytics
    mock-graph/            # Microsoft Graph API (service principals, licenses, M365 usage)
  scripts/
    seed-mock-services.sh  # Register test users and configure login
  docker-compose.yml       # Orchestrates all 8 services
  .env.example             # Environment variable template
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values. The defaults work for local development.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://techdebt:techdebt@db:5432/techdebt` | PostgreSQL connection string |
| `JWT_SECRET` | Yes | *(generate one)* | Secret key for signing auth tokens. Generate with `openssl rand -hex 32` |
| `OIDC_ISSUER_URL` | Yes | `http://mock-oidc:10090` | Identity provider URL (mock-oidc for local dev) |
| `OIDC_CLIENT_ID` | Yes | `mock-oidc-client` | OIDC client identifier |
| `OIDC_CLIENT_SECRET` | Yes | `mock-oidc-secret` | OIDC client secret |
| `FRONTEND_URL` | Yes | `http://localhost:3100` | Where the frontend is accessible |
| `BACKEND_URL` | Yes | `http://localhost:8100` | Where the backend is accessible |
| `ENFORCE_SECRETS` | No | `false` | Set to `true` in production to require strong secrets |
| `LOG_BUFFER_SIZE` | No | `10000` | Max activity log entries kept in memory |

### Data Source URLs (Auto-configured in Docker)

| Variable | Default | Service |
|----------|---------|---------|
| `WORKDAY_BASE_URL` | `http://mock-workday:9001` | Procurement data |
| `AUDITBOARD_BASE_URL` | `http://mock-auditboard:9002` | Vendor risk data |
| `ENTRA_ID_BASE_URL` | `http://mock-entra:9003` | Identity analytics |
| `TAILSPEND_BASE_URL` | `http://mock-tailspend:9004` | Spend analytics |
| `GRAPH_BASE_URL` | `http://mock-graph:9005` | Microsoft Graph API |

---

## Production Deployment

For production, you'll need to:

1. **Replace mock-oidc** with your real identity provider (Azure AD, Okta, etc.)
   - Set `OIDC_ISSUER_URL`, `OIDC_CLIENT_ID`, and `OIDC_CLIENT_SECRET` to your provider's values
2. **Replace mock services** with real API connections
   - Update the `*_BASE_URL` variables to point to your actual Workday, AuditBoard, Entra ID, etc.
3. **Use a managed PostgreSQL** database
   - Update `DATABASE_URL` to your production connection string
4. **Set `ENFORCE_SECRETS=true`** to require strong JWT and OIDC secrets at startup
5. **Generate a strong `JWT_SECRET`** with `openssl rand -hex 32`

The mock services are for local development only and are not included in production deployments (they're behind the `dev` Docker Compose profile).

---

## Troubleshooting

**"redirect_uri not registered for client"**
Run `bash scripts/seed-mock-services.sh` to register the login redirect URI. This is needed after container recreation.

**A service shows as "unhealthy"**
Check its logs: `docker compose --profile dev logs <service-name>`. Common causes: port conflict, missing dependency, or a previous container didn't shut down cleanly. Try `docker compose --profile dev down && docker compose --profile dev up -d`.

**Port already in use**
Another app is using one of TechDebt's ports. Check with `lsof -i :3100` (or whichever port). Either stop the other app or modify the port mapping in `docker-compose.yml`.

**Login page shows no users**
Run the seed script: `bash scripts/seed-mock-services.sh`

**Database seems empty or stale**
The database is initialized via Alembic migrations on first startup. To reset: `docker compose --profile dev down -v` then start fresh.

---

## License

See [LICENSE](LICENSE) for details.
