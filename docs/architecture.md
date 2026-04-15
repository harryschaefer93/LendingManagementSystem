# Lending Management System (LMS) -- Architecture Overview

> Azure-hosted loan origination workflow with role-based access, document management, and audit trail.

```mermaid
graph LR
    %% ───────────────────────────────────────────────
    %% Actors
    %% ───────────────────────────────────────────────
    subgraph Users["👤 Users (Browser)"]
        Officer["Loan Officer"]
        Underwriter["Underwriter"]
        Admin["Admin"]
    end

    %% ───────────────────────────────────────────────
    %% Frontend Tier
    %% ───────────────────────────────────────────────
    subgraph Frontend["Frontend Tier"]
        SWA["Azure Static Web App\n(Free)\nReact + TypeScript SPA"]
    end

    %% ───────────────────────────────────────────────
    %% Security & Identity
    %% ───────────────────────────────────────────────
    subgraph Security["Security & Identity"]
        Entra["Microsoft Entra ID\nApp Roles: Officer,\nUnderwriter, Admin"]
        KV["Azure Key Vault\n(Standard)\nDB + Storage secrets"]
    end

    %% ───────────────────────────────────────────────
    %% Backend Tier
    %% ───────────────────────────────────────────────
    subgraph Backend["Backend Tier"]
        API["Azure App Service\n(B1 Linux)\nFastAPI Python API\nManaged Identity"]
    end

    %% ───────────────────────────────────────────────
    %% Data Tier
    %% ───────────────────────────────────────────────
    subgraph Data["Data Tier"]
        PG["Azure PostgreSQL\nFlexible Server (B1ms)\nloans · documents\ndecisions · audit_log"]
        Blob["Azure Blob Storage\n(Standard LRS)\nContainer: documents"]
    end

    %% ───────────────────────────────────────────────
    %% Observability
    %% ───────────────────────────────────────────────
    subgraph Observability["Observability"]
        AppIns["Application Insights"]
        LAW["Log Analytics\nWorkspace"]
    end

    %% ───────────────────────────────────────────────
    %% Data Flow
    %% ───────────────────────────────────────────────

    %% ① Users → Frontend
    Officer  -- "HTTPS" --> SWA
    Underwriter -- "HTTPS" --> SWA
    Admin -- "HTTPS" --> SWA

    %% ② Auth flow
    SWA -- "① MSAL.js login" --> Entra
    Entra -- "JWT (access token)" --> SWA

    %% ③ Frontend → Backend
    SWA -- "② HTTPS + JWT\n/api/loans\n/api/documents\n/api/decide" --> API

    %% ④ Backend → Data
    API -- "③ SQL (TLS)\nCRUD + audit log" --> PG
    API -- "④ REST + SAS tokens\nupload / download" --> Blob

    %% ⑤ Backend → Security
    API -- "⑤ Managed Identity\nKey Vault references" --> KV

    %% ⑥ Backend → Observability
    API -- "⑥ Telemetry\nOpenTelemetry SDK" --> AppIns
    AppIns -- "log ingestion" --> LAW

    %% ───────────────────────────────────────────────
    %% Styles
    %% ───────────────────────────────────────────────
    classDef frontend fill:#50e6ff,stroke:#0078d4,color:#000
    classDef backend fill:#0078d4,stroke:#005a9e,color:#fff
    classDef data fill:#7fba00,stroke:#5e8c00,color:#000
    classDef security fill:#ffb900,stroke:#d48c00,color:#000
    classDef observability fill:#b4a0ff,stroke:#7b64c0,color:#000
    classDef users fill:#f2f2f2,stroke:#7f7f7f,color:#000

    class SWA frontend
    class API backend
    class PG,Blob data
    class Entra,KV security
    class AppIns,LAW observability
    class Officer,Underwriter,Admin users
```

## Key Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Frontend hosting** | Static Web App (Free) | Zero-cost SPA hosting with built-in CI/CD and custom domain support |
| **Backend hosting** | App Service B1 Linux | Right-sized for POC load; easy scaling path to P1v3 for production |
| **Database** | PostgreSQL Flexible Server B1ms | Managed Postgres with Entra auth support; 2 vCores sufficient for POC |
| **Secret management** | Key Vault references | No secrets in app config -- App Service resolves `@Microsoft.KeyVault(...)` at runtime |
| **Auth pattern** | Entra ID + MSAL.js + JWT | Enterprise SSO; role-based access via app roles (Officer, Underwriter, Admin) |
| **Document storage** | Blob Storage + SAS tokens | Cost-effective binary storage; time-limited SAS URLs for secure download |
| **Observability** | Application Insights + Log Analytics | Turnkey APM with distributed tracing and KQL query support |
