targetScope = 'subscription'

// ──────────────────────────────────────────────
// Parameters
// ──────────────────────────────────────────────

@description('Resource name prefix used for all resources')
param prefix string = 'lmspoc'

@description('Azure region for deployment')
param location string = 'eastus2'

@description('PostgreSQL administrator login name')
param postgresAdminUser string = 'lmsadmin'

@secure()
@description('PostgreSQL administrator password')
param postgresAdminPassword string

@description('Environment tag value')
param environment string = 'poc'

@description('Owner tag value')
param owner string = 'lms-team'

// ──────────────────────────────────────────────
// Variables
// ──────────────────────────────────────────────

var tags = {
  project: 'lms-poc'
  environment: environment
  owner: owner
}

var resourceGroupName = 'rg-${prefix}-${environment}'

// ──────────────────────────────────────────────
// Resource Group
// ──────────────────────────────────────────────

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// ──────────────────────────────────────────────
// Module: Monitoring (Log Analytics + App Insights)
// ──────────────────────────────────────────────

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
  }
}

// ──────────────────────────────────────────────
// Module: Storage Account
// ──────────────────────────────────────────────

module storage 'modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
  }
}

// ──────────────────────────────────────────────
// Module: PostgreSQL Flexible Server
// ──────────────────────────────────────────────

module postgresql 'modules/postgresql.bicep' = {
  name: 'postgresql'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
    adminUser: postgresAdminUser
    adminPassword: postgresAdminPassword
  }
}

// ──────────────────────────────────────────────
// Module: Static Web App (Frontend)
// ──────────────────────────────────────────────

module frontendSwa 'modules/staticwebapp.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
  }
}

// ──────────────────────────────────────────────
// Module: Backend App Service
// ──────────────────────────────────────────────

module backend 'modules/appservice.bicep' = {
  name: 'backend'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    appInsightsInstrumentationKey: monitoring.outputs.appInsightsInstrumentationKey
    staticWebAppHostname: frontendSwa.outputs.defaultHostname
  }
}

// ──────────────────────────────────────────────
// Module: Key Vault
// ──────────────────────────────────────────────

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    prefix: prefix
    location: location
    tags: tags
    appServicePrincipalId: backend.outputs.appServicePrincipalId
    postgresConnectionString: 'postgresql+asyncpg://${postgresAdminUser}:${postgresAdminPassword}@${postgresql.outputs.fqdn}:5432/lms?ssl=require'
    storageConnectionString: storage.outputs.connectionString
  }
}

// ──────────────────────────────────────────────
// Module: Configure App Service with Key Vault refs
// ──────────────────────────────────────────────

module backendConfig 'modules/appservice-config.bicep' = {
  name: 'backend-config'
  scope: rg
  params: {
    appServiceName: backend.outputs.appServiceName
    keyVaultName: keyVault.outputs.keyVaultName
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    appInsightsInstrumentationKey: monitoring.outputs.appInsightsInstrumentationKey
    staticWebAppHostname: frontendSwa.outputs.defaultHostname
  }
}

// ──────────────────────────────────────────────
// Outputs
// ──────────────────────────────────────────────

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_BACKEND_URL string = backend.outputs.appServiceUrl
output AZURE_FRONTEND_URL string = 'https://${frontendSwa.outputs.defaultHostname}'
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.storageAccountName
output AZURE_KEYVAULT_NAME string = keyVault.outputs.keyVaultName
output AZURE_POSTGRESQL_FQDN string = postgresql.outputs.fqdn
output AZURE_APPINSIGHTS_NAME string = monitoring.outputs.appInsightsName
