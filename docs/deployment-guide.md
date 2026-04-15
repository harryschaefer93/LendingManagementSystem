# Deployment Guide

This guide covers deploying the Lending Management System (LMS) POC to Azure using the Azure Developer CLI (`azd`).

## Prerequisites

| Requirement | Minimum Version | Install |
|-------------|----------------|---------|
| Azure Subscription | -- | [Create free account](https://azure.microsoft.com/free/) |
| Azure CLI | 2.60+ | [Install](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| Azure Developer CLI | 1.9+ | [Install](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) |
| Python | 3.11+ | [Download](https://www.python.org/downloads/) |
| Node.js | 18+ | [Download](https://nodejs.org/) |

## Step 1: Configure Environment

### Set the database password

The PostgreSQL admin password is read from the `POSTGRES_ADMIN_PASSWORD` environment variable at deploy time.

```bash
# Bash / macOS / Linux
export POSTGRES_ADMIN_PASSWORD="<your-secure-password>"

# PowerShell
$env:POSTGRES_ADMIN_PASSWORD = "<your-secure-password>"
```

> **Tip**: Use a strong password (16+ characters, mixed case, numbers, symbols). This password is stored in Azure Key Vault after deployment.

### Customize deployment parameters (optional)

Edit `infra/main.bicepparam` to change defaults:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prefix` | `lmspoc` | Resource name prefix (keep short, lowercase, no hyphens) |
| `location` | `eastus2` | Azure region for all resources |
| `postgresAdminUser` | `lmsadmin` | PostgreSQL admin username |
| `environment` | `poc` | Environment tag value |
| `owner` | `lms-team` | Owner tag value |

## Step 2: Deploy with azd

### Authenticate

```bash
az login
azd auth login
```

### Deploy all resources

```bash
azd up
```

On first run, `azd` will prompt for:
- **Environment name**: A name for this deployment (e.g., `lms-dev`)
- **Azure subscription**: Select from your available subscriptions
- **Azure location**: Confirm or change the deployment region

The deployment creates the following Azure resources:

| Resource | Type | SKU | Name Pattern |
|----------|------|-----|-------------|
| Resource Group | `Microsoft.Resources/resourceGroups` | -- | `rg-lmspoc-poc` |
| App Service Plan + App | `Microsoft.Web/sites` | B1 Linux | `app-lmspoc-*` |
| Static Web App | `Microsoft.Web/staticSites` | Free | `swa-lmspoc-*` |
| PostgreSQL Flexible Server | `Microsoft.DBforPostgreSQL/flexibleServers` | B1ms | `psql-lmspoc-*` |
| Storage Account | `Microsoft.Storage/storageAccounts` | Standard LRS | `stlmspoc*` |
| Key Vault | `Microsoft.KeyVault/vaults` | Standard | `kv-lmspoc-*` |
| Application Insights | `Microsoft.Insights/components` | -- | `appi-lmspoc-*` |
| Log Analytics Workspace | `Microsoft.OperationalInsights/workspaces` | -- | `law-lmspoc-*` |

Deployment takes approximately **5 minutes** on first run. Subsequent deploys (code-only) are faster.

### What happens during deployment

1. **Infrastructure provisioning**: Bicep templates create all Azure resources
2. **Backend deployment**: Python app is packaged and deployed to App Service
3. **Frontend deployment**: React app is built and deployed to Static Web App
4. **Configuration**: App Service receives Key Vault references for database and storage secrets
5. **Startup**: App Service runs `startup.sh` which executes `alembic upgrade head` then starts uvicorn

## Step 3: Verify Deployment

After `azd up` completes, it outputs the deployed URLs.

### Check the backend health endpoint

```bash
curl https://<AZURE_BACKEND_URL>/api/health
```

Expected response:

```json
{"status": "healthy", "database": "connected"}
```

### Check the frontend

Open the `AZURE_FRONTEND_URL` in a browser. The React SPA should load and display the loan list (empty until data is seeded).

### View deployment outputs

```bash
azd env get-values
```

This prints all output variables including `AZURE_BACKEND_URL`, `AZURE_FRONTEND_URL`, `AZURE_KEYVAULT_NAME`, etc.

## Step 4: Seed Demo Data

The App Service `startup.sh` runs Alembic migrations automatically on each deploy. To seed demo data into the Azure-hosted database, run the seed script against the deployed backend:

### Option A: Via App Service SSH

```bash
# Open an SSH session to the App Service
az webapp ssh --name <app-service-name> --resource-group rg-lmspoc-poc

# Inside the SSH session:
python -m app.seed
```

### Option B: Via local script with remote database

```bash
cd backend

# Set DATABASE_URL to the Azure PostgreSQL connection string
# Find it in Key Vault or construct it from the deployment outputs:
export DATABASE_URL="postgresql+asyncpg://lmsadmin:<password>@<AZURE_POSTGRESQL_FQDN>:5432/lms?ssl=require"

python -m app.seed
```

> **Note**: For Option B, your local IP must be allowed through the PostgreSQL firewall. Add it via the Azure Portal or Azure CLI.

## Step 5: Configure Entra ID (Optional)

By default, the POC runs in **mock authentication mode**. To enable Microsoft Entra ID authentication:

### 5.1 Create an App Registration

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Set the name (e.g., `lms-poc`)
3. Set **Redirect URI** to:
   - Type: **Single-page application (SPA)**
   - URI: `https://<AZURE_FRONTEND_URL>/`
4. Note the **Application (client) ID** and **Directory (tenant) ID**

### 5.2 Define App Roles

In the app registration, go to **App roles** → **Create app role** and create three roles:

| Display Name | Value | Allowed Member Types |
|-------------|-------|---------------------|
| Loan Officer | `officer` | Users/Groups |
| Underwriter | `underwriter` | Users/Groups |
| Admin | `admin` | Users/Groups |

### 5.3 Assign Users to Roles

Go to **Enterprise applications** → select the app → **Users and groups** → **Add user/group**. Assign users to their appropriate roles.

### 5.4 Configure the Backend

Set the following environment variables on the App Service:

```bash
az webapp config appsettings set \
  --name <app-service-name> \
  --resource-group rg-lmspoc-poc \
  --settings \
    AUTH_MODE=entra \
    ENTRA_TENANT_ID=<your-tenant-id> \
    ENTRA_CLIENT_ID=<your-client-id>
```

### 5.5 Configure the Frontend

Update the frontend environment to include MSAL configuration. The React SPA uses `@azure/msal-browser` for token acquisition. Set `VITE_ENTRA_TENANT_ID` and `VITE_ENTRA_CLIENT_ID` as build-time environment variables or in a `.env.production` file.

### 5.6 Restart and Verify

```bash
az webapp restart --name <app-service-name> --resource-group rg-lmspoc-poc
```

Navigate to the frontend URL. You should be redirected to the Microsoft login page. After authentication, the app reads your assigned role from the JWT token's `roles` claim.

## Teardown

To delete **all** Azure resources created by this deployment:

```bash
azd down --purge
```

The `--purge` flag ensures soft-deleted resources (Key Vault) are permanently removed. This deletes:
- The resource group and all resources within it
- All data in PostgreSQL and Blob Storage
- All secrets in Key Vault
- Application Insights data

> **Warning**: This action is irreversible. All data will be permanently deleted.

## Troubleshooting

### CORS Errors

**Symptom**: Browser console shows `Access-Control-Allow-Origin` errors.

**Cause**: The frontend origin is not in the backend's `CORS_ORIGINS` setting.

**Fix**: Update the `CORS_ORIGINS` app setting on the App Service to include the Static Web App URL:

```bash
az webapp config appsettings set \
  --name <app-service-name> \
  --resource-group rg-lmspoc-poc \
  --settings CORS_ORIGINS="https://<static-web-app-hostname>"
```

> The Bicep templates configure this automatically. If you see CORS errors, verify the Static Web App hostname matches what's in the app settings.

### Database Connection Failures

**Symptom**: `/api/health` returns `{"status": "unhealthy", "database": "disconnected"}`.

**Possible causes**:
1. **Key Vault reference not resolving**: Check that the App Service managed identity has `Get` secret permissions on Key Vault
2. **PostgreSQL firewall**: Ensure the App Service outbound IPs are allowed. The Bicep template configures `allowAllAzureIPs` by default
3. **Wrong password**: Verify `POSTGRES_ADMIN_PASSWORD` was set correctly before running `azd up`

**Diagnostics**:

```bash
# Check App Service logs
az webapp log tail --name <app-service-name> --resource-group rg-lmspoc-poc

# Verify Key Vault secret exists
az keyvault secret show --vault-name <keyvault-name> --name database-url
```

### Blob Storage 403 Forbidden

**Symptom**: Document upload/download returns 403 errors.

**Possible causes**:
1. **Storage connection string incorrect**: Verify the Key Vault secret `storage-connection-string` contains a valid connection string
2. **Container does not exist**: The `documents` container must exist in the storage account. Create it manually if the seed script hasn't run:

```bash
az storage container create \
  --name documents \
  --account-name <storage-account-name> \
  --auth-mode login
```

### App Service Not Starting

**Symptom**: App Service returns 502 or 503 errors.

**Diagnostics**:

```bash
# View startup logs
az webapp log tail --name <app-service-name> --resource-group rg-lmspoc-poc

# Check if the startup command is configured
az webapp config show --name <app-service-name> --resource-group rg-lmspoc-poc --query "linuxFxVersion"
```

**Common fixes**:
- Ensure `startup.sh` has Unix line endings (LF, not CRLF)
- Verify Python 3.11 runtime is selected on the App Service
- Check that `requirements.txt` installs without errors
