using './main.bicep'

param prefix = 'lmspoc'
param location = 'eastus2'
param postgresAdminUser = 'lmsadmin'
param postgresAdminPassword = readEnvironmentVariable('POSTGRES_ADMIN_PASSWORD', '')
param environment = 'poc'
param owner = 'lms-team'
