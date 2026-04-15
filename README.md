# Lending Management System (LMS) -- POC

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fharryschaefer93%2FLendingManagementSystem-%2Fmain%2Finfra%2Fmain.json)

A web-based proof-of-concept for internal loan lifecycle management, built on Azure with a modern React + FastAPI stack. It demonstrates end-to-end loan origination -- from application creation through underwriting decision -- with document management, role-based access control, and a full audit trail.

## Features

- **Loan Application CRUD** -- Create, edit, and view loan applications with borrower details, loan type, amount, and term
- **Workflow Engine** -- Manual status transitions: Draft → Submitted → In Review → Approved / Declined
- **Document Management** -- Upload, attach, and download documents (ID, income proof, property docs) via Azure Blob Storage
- **Underwriting Decisions** -- Record approve/decline decisions with notes and optional conditions
- **Role-Based Access Control** -- Three roles (Loan Officer, Underwriter, Admin) with enforced permissions
- **Audit Trail** -- All status changes and decisions logged with timestamps and actor identity
- **Search & Filtering** -- List loans with filters by status, date, and loan officer
- **Synthetic Demo Data** -- Pre-seeded loan records for immediate demonstration

## Screenshots

### Loans Dashboard
View all loans with color-coded status badges, filters, and role-aware actions.

![Loans Dashboard](docs/screenshots/01-loan-dashboard.png)

### Loan Detail View
Full loan details with decision record, borrower info, and tabbed navigation.

![Loan Detail](docs/screenshots/02-loan-detail.png)

### Audit Trail
Complete timeline of all status changes and decisions with actor and timestamp.

![Audit Trail](docs/screenshots/03-audit-trail.png)

### Create Loan Application
Loan Officers can create new applications with borrower details, type, amount, and term.

![Create Loan](docs/screenshots/04-create-loan.png)

### Underwriter Decision View
Underwriters see Approve/Decline actions with notes and conditions fields for loans In Review.

![Underwriter Review](docs/screenshots/05-underwriter-review.png)

### API Documentation (Swagger)
FastAPI auto-generated interactive API docs with all 13 endpoints.

![Swagger API](docs/screenshots/06-swagger-api.png)

## Architecture

The system uses a three-tier architecture deployed to Azure:

```
Browser → Static Web App (React SPA) → App Service (FastAPI API) → PostgreSQL + Blob Storage
```

See [docs/architecture.md](docs/architecture.md) for the full architecture diagram, data flow, and design decisions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite 6 |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL 16 via SQLAlchemy (async) + Alembic migrations |
| Document Storage | Azure Blob Storage |
| Authentication | Microsoft Entra ID (with mock mode for local dev) |
| Infrastructure as Code | Bicep + Azure Developer CLI (`azd`) |
| Observability | Application Insights + Log Analytics |
| Secret Management | Azure Key Vault (Key Vault references) |

## Project Structure

```
├── backend/                  # FastAPI Python API
│   ├── app/
│   │   ├── main.py           # FastAPI app entrypoint
│   │   ├── config.py         # Pydantic settings (env vars)
│   │   ├── database.py       # SQLAlchemy async engine + session
│   │   ├── seed.py           # Synthetic demo data loader
│   │   ├── auth/             # Auth dependencies + role enforcement
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # API route handlers
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Business logic layer
│   ├── alembic/              # Database migration scripts
│   ├── requirements.txt
│   └── startup.sh            # Azure App Service startup script
├── frontend/                 # React TypeScript SPA
│   ├── src/
│   │   ├── api/              # Axios API client
│   │   ├── components/       # UI components (loans, documents, layout)
│   │   ├── contexts/         # React context (auth)
│   │   ├── hooks/            # Custom hooks (useLoans, useDocuments)
│   │   ├── styles/           # Global CSS
│   │   └── types/            # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
├── infra/                    # Bicep IaC modules
│   ├── main.bicep            # Root deployment (subscription scope)
│   ├── main.bicepparam       # Parameter file
│   └── modules/              # Individual resource modules
├── docs/                     # Architecture and deployment docs
└── azure.yaml                # Azure Developer CLI configuration
```

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 16 (local instance for development)
- **Azure CLI** (`az`) -- for Azure deployment
- **Azure Developer CLI** (`azd`) -- for one-command deployment (optional)

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone <repository-url>
cd lms-poc
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a local PostgreSQL database named `lms`, then run migrations and seed data:

```bash
# Ensure PostgreSQL is running and a database named 'lms' exists
# Default connection: postgresql+asyncpg://lmsadmin:password@localhost:5432/lms
# Override with DATABASE_URL env var if needed

alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the application

Navigate to **http://localhost:3000**. The Vite dev server proxies `/api` requests to the backend at `http://localhost:8000`.

### 5. Switch roles

Use the **role switcher** in the header to switch between Loan Officer, Underwriter, and Admin. Each role sees different actions and permissions.

## Azure Deployment

### 1. Authenticate

```bash
az login
azd auth login
```

### 2. Set the database password

```bash
# Bash / macOS / Linux
export POSTGRES_ADMIN_PASSWORD="<your-secure-password>"

# PowerShell
$env:POSTGRES_ADMIN_PASSWORD = "<your-secure-password>"
```

### 3. Deploy

```bash
azd up
```

This creates the following Azure resources (~5 minutes on first deploy):

| Resource | SKU | Purpose |
|----------|-----|---------|
| Resource Group | -- | `rg-lmspoc-poc` |
| App Service (Linux) | B1 | FastAPI backend API |
| Static Web App | Free | React frontend SPA |
| PostgreSQL Flexible Server | B1ms | Relational data store |
| Storage Account | Standard LRS | Document blob storage |
| Key Vault | Standard | Secret management |
| Application Insights | -- | APM and telemetry |
| Log Analytics Workspace | -- | Centralized logging |

### 4. Verify

After deployment completes, `azd` prints the frontend and backend URLs. Verify the backend health endpoint:

```bash
curl https://<backend-url>/api/health
# Expected: {"status":"healthy","database":"connected"}
```

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for the interactive Swagger UI, or **http://localhost:8000/redoc** for ReDoc-style documentation.

Key API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check (database connectivity) |
| `GET` | `/api/loans` | List loans (with query filters) |
| `POST` | `/api/loans` | Create a new loan application |
| `GET` | `/api/loans/{id}` | Get loan details with decisions and audit log |
| `PATCH` | `/api/loans/{id}/status` | Transition loan status |
| `POST` | `/api/documents/upload` | Upload a document |
| `GET` | `/api/documents/{loan_id}` | List documents for a loan |
| `GET` | `/api/me` | Get current user info |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://lmsadmin:password@localhost:5432/lms` |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string | _(empty -- documents disabled when unset)_ |
| `AZURE_STORAGE_CONTAINER_NAME` | Blob container name for documents | `documents` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `AUTH_MODE` | Authentication mode: `mock` or `entra` | `mock` |
| `ENTRA_TENANT_ID` | Microsoft Entra ID tenant ID | _(empty)_ |
| `ENTRA_CLIENT_ID` | Microsoft Entra ID app registration client ID | _(empty)_ |
| `VITE_API_URL` | Backend API URL for production frontend builds | _(set automatically by azd)_ |

## Mock Authentication

For local development, the app runs in **mock auth mode** (`AUTH_MODE=mock`) with a built-in role switcher:

- The frontend header includes a **role selector** to switch between Officer, Underwriter, and Admin
- Each role switch sends an `X-Mock-User` header with a JSON payload: `{"id": "officer-1", "name": "Jane Smith", "role": "officer"}`
- If no header is provided, the backend defaults to a Loan Officer user

To activate **real Entra ID authentication**, set `AUTH_MODE=entra` and configure `ENTRA_TENANT_ID` and `ENTRA_CLIENT_ID`. See [docs/deployment-guide.md](docs/deployment-guide.md#step-5-configure-entra-id-optional) for setup instructions.

## Clean Up

To remove all Azure resources:

```bash
azd down --purge
```

This deletes the resource group and all resources within it, including any data in PostgreSQL and Blob Storage.

## License

[MIT](LICENSE)
