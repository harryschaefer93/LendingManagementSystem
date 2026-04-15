@description('Resource name prefix')
param prefix string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('PostgreSQL administrator login')
param adminUser string

@secure()
@description('PostgreSQL administrator password')
param adminPassword string

// ──────────────────────────────────────────────
// PostgreSQL Flexible Server
// ──────────────────────────────────────────────

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: 'psql-${prefix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: adminUser
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// ──────────────────────────────────────────────
// Database: lms
// ──────────────────────────────────────────────

resource lmsDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgresServer
  name: 'lms'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// ──────────────────────────────────────────────
// SSL enforcement
// ──────────────────────────────────────────────

resource requireSecureTransport 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  parent: postgresServer
  name: 'require_secure_transport'
  properties: {
    value: 'on'
    source: 'user-override'
  }
}

// ──────────────────────────────────────────────
// Firewall: Allow Azure services
// ──────────────────────────────────────────────

resource allowAzureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// ──────────────────────────────────────────────
// Outputs
// ──────────────────────────────────────────────

output serverId string = postgresServer.id
output serverName string = postgresServer.name
output fqdn string = postgresServer.properties.fullyQualifiedDomainName
