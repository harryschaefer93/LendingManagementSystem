@description('Name of the existing App Service')
param appServiceName string

@description('Name of the Key Vault')
param keyVaultName string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Application Insights instrumentation key')
param appInsightsInstrumentationKey string

@description('Static Web App hostname for CORS')
param staticWebAppHostname string

// ──────────────────────────────────────────────
// Reference existing App Service
// ──────────────────────────────────────────────

resource appService 'Microsoft.Web/sites@2023-12-01' existing = {
  name: appServiceName
}

// ──────────────────────────────────────────────
// App Settings with Key Vault References
// ──────────────────────────────────────────────

resource appSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: appService
  name: 'appsettings'
  properties: {
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    APPLICATIONINSIGHTS_CONNECTION_STRING: appInsightsConnectionString
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsightsInstrumentationKey
    DATABASE_URL: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=postgres-connection-string)'
    AZURE_STORAGE_CONNECTION_STRING: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=storage-connection-string)'
    CORS_ORIGINS: 'https://${staticWebAppHostname}'
    AUTH_MODE: 'mock'
    AZURE_STORAGE_CONTAINER_NAME: 'documents'
  }
}
