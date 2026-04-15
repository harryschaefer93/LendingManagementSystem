# BRIEF.md -- Lending Management System (LMS) POC

## 1. Executive Summary

This POC demonstrates a web-based Lending Management System (LMS) for internal loan lifecycle management. It provides an end-to-end loan workflow -- from application creation through underwriting decision -- with document management, role-based access, and audit logging. Built on Azure with a modern React + FastAPI stack, it serves as a foundation for production-ready lending solutions.

## 2. Project Context

- **Type**: Reference implementation / POC
- **Industry**: Financial Services (Lending)
- **Users**: Internal -- Loan Officers, Underwriters, Admins

### Business Problem

Organizations managing loans need a unified, modern system to track loans through their lifecycle. Loan officers, underwriters, and operations staff need a centralized tool to create applications, manage documents, record decisions, and maintain an audit trail.

### Target Users

| Role | Responsibilities |
|------|-----------------|
| Loan Officer | Create and submit loan applications, upload documents |
| Underwriter | Review loans, make approve/decline decisions |
| Admin | View all loans, documents, audit logs (read-only oversight) |

## 3. POC Scope

### In Scope

- **Loan Application CRUD**: Create, save draft, submit, and view loan applications with borrower details, loan type, amount, and term
- **Loan Workflow**: Manual status transitions (Draft → Submitted → In Review → Approved / Declined) with role-appropriate access
- **Document Management**: Upload, attach, view, and download documents (ID, income proof, property docs) with basic metadata
- **Underwriting Decision**: Record decision (Approve/Decline), notes, and optional conditions
- **Search & Filtering**: List all loans with filters by status, date, and loan officer
- **Role-Based Access Control**: Three roles -- Loan Officer, Underwriter, Admin
- **Audit Trail**: Log status changes and underwriting decisions with timestamps and actor
- **Synthetic Demo Data**: Pre-seeded loan records for demonstration

### Out of Scope

- Automated credit scoring or rules engine
- External bureau integrations (credit, identity verification)
- Payment processing or loan servicing
- Customer-facing self-service portal
- Regulatory reporting
- SLA tracking or workflow automation
- Production hardening (HA, DR, performance tuning)
- Mobile-native UI

### Assumptions & Dependencies

- POC uses **synthetic data only** -- no real borrower PII
- Authentication uses Microsoft Entra ID (mock mode available for local development)
- Team has access to an Azure subscription for deployment

## 4. Objectives

1. **Demonstrate end-to-end loan lifecycle**: A loan can be created, submitted, reviewed, and approved/declined through the UI
2. **Validate document management**: Documents can be uploaded, attached to loans, and viewed/downloaded
3. **Prove role-based access model**: Three distinct roles with appropriate access controls are functional
4. **Show audit trail capability**: All status changes and decisions are logged and queryable
5. **Deliver demoable POC**: Complete workflow is demonstrable end-to-end in under 5 minutes

## 5. Success Criteria

| # | Criterion | Type |
|---|-----------|------|
| S1 | A loan can be created, moved through all status stages, and retrieved with full history | Quantitative |
| S2 | At least 3 document types can be uploaded and viewed against a loan record | Quantitative |
| S3 | Each role (Officer, Underwriter, Admin) sees only role-appropriate actions | Quantitative |
| S4 | Audit log captures all status changes and decisions with actor + timestamp | Quantitative |
| S5 | Page load times are under 3 seconds for all screens | Quantitative |
| S6 | End-to-end demo (create → approve → retrieve) completes in under 5 minutes | Quantitative |

## 6. Acceptance Criteria

### Objective 1: End-to-End Loan Lifecycle

- [ ] AC-1.1: A Loan Officer can create a new loan application with borrower name, loan type, amount, and term
- [ ] AC-1.2: A Loan Officer can save a loan as Draft and later submit it (status changes to Submitted)
- [ ] AC-1.3: An Underwriter can move a Submitted loan to In Review
- [ ] AC-1.4: An Underwriter can Approve or Decline a loan In Review, recording notes and optional conditions
- [ ] AC-1.5: An Admin can view any loan and its full status history
- [ ] AC-1.6: Status transitions are enforced (e.g., cannot go from Draft directly to Approved)

### Objective 2: Document Management

- [ ] AC-2.1: A user can upload a document (PDF, JPEG, PNG up to 10MB) and attach it to a loan
- [ ] AC-2.2: Uploaded documents display metadata: document type, upload date, filename
- [ ] AC-2.3: A user can view/download any document attached to a loan they have access to
- [ ] AC-2.4: At least 3 document type categories are supported (ID, Income Proof, Property)

### Objective 3: Role-Based Access

- [ ] AC-3.1: Loan Officers can create/edit loans and upload documents but cannot record underwriting decisions
- [ ] AC-3.2: Underwriters can review loans, upload documents, and record decisions but cannot create new loans
- [ ] AC-3.3: Admins have read access to all loans, documents, and audit logs
- [ ] AC-3.4: Unauthenticated users cannot access any part of the application

### Objective 4: Audit Trail

- [ ] AC-4.1: Every status change records: previous status, new status, actor, timestamp
- [ ] AC-4.2: Every underwriting decision records: decision, underwriter, timestamp, notes
- [ ] AC-4.3: Audit log entries are immutable (append-only)
- [ ] AC-4.4: An Admin can view the audit trail for any loan

### Objective 5: Demoable POC

- [ ] AC-5.1: Application loads and renders the loan list within 3 seconds
- [ ] AC-5.2: Pre-seeded synthetic data exists for at least 10 sample loans in various statuses
- [ ] AC-5.3: Full demo flow (create loan → upload doc → submit → review → decide → retrieve) completes in under 5 minutes

## 7. Architecture

### Azure Services

| Service | Purpose | SKU / Tier |
|---------|---------|------------|
| **Azure App Service** | Host FastAPI backend API | B1 (POC) |
| **Azure Static Web App** | Host React frontend | Free |
| **Azure Database for PostgreSQL -- Flexible Server** | Relational data store for loans, decisions, audit log | Burstable B1ms (POC) |
| **Azure Blob Storage** | Document storage (uploaded files) | Standard LRS |
| **Microsoft Entra ID** | Authentication and role-based access control | Included |
| **Azure Monitor + Application Insights** | Observability, performance tracking | Free tier |
| **Azure Key Vault** | Store connection strings and secrets | Standard |

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + TypeScript (Vite) | Modern SPA, fast builds, large ecosystem |
| Backend API | Python (FastAPI) | Auto-generated API docs, Pydantic validation, async-native |
| Database | PostgreSQL (async via SQLAlchemy + asyncpg) | Relational model, strong Azure managed option |
| Auth | Mock mode (dev) / MSAL.js + Entra ID (production) | Native Azure identity; supports app roles for RBAC |
| File Storage | Azure Blob Storage SDK | Scalable document storage with SAS token access |
| IaC | Bicep + azd | Azure-native, first-class deployment support |

### Integration Points

- **Entra ID**: App registration with three app roles (Officer, Underwriter, Admin)
- **Blob Storage**: Backend generates SAS tokens for secure upload/download -- frontend never accesses storage directly
- **PostgreSQL**: Backend API is the sole accessor; no direct DB access from frontend
- **Key Vault**: Connection strings stored as secrets, referenced by App Service via managed identity

## 8. Risks & Mitigations

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| R1 | **Data sensitivity** -- Architecture must handle PII-grade data in production | High | Medium | Design storage and access patterns as if handling real PII from day one (encryption at rest, TLS in transit, RBAC on all resources). |
| R2 | **Compliance** -- Lending apps often fall under regulatory frameworks (PIPEDA, OSFI, SOX, etc.) | High | Medium | Use Entra ID for auth. Document the gap between POC config and production compliance requirements (Private Endpoints, audit log retention, CMK). |
| R3 | **Scope creep** -- Future enhancements (credit bureau integration, AI doc review) could bleed into POC | High | Medium | BRIEF.md explicitly defines scope boundaries. Any additions require a scope change conversation. |
| R4 | **Entra ID tenant access** -- POC auth depends on Entra ID app registration | Medium | Low | Built-in mock auth mode for development. Fall back to a demo tenant if primary tenant is unavailable. |

## 9. Getting Started

See [README.md](README.md) for setup and deployment instructions.
