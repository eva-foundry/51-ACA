// EVA-STORY: ACA-01-010
// EVA-STORY: ACA-12-009
// EVA-STORY: ACA-12-010
// EVA-STORY: ACA-12-011
// EVA-STORY: ACA-12-012
// EVA-STORY: ACA-12-013
// EVA-STORY: ACA-12-014
// EVA-STORY: ACA-12-015
// EVA-STORY: ACA-12-016
// Phase 1 -- marco* sandbox wiring
// Creates: Cosmos DB containers, Key Vault references
// Assumes: marco-cosmos, marco-kv already exist in EsDAICoE-Sandbox
// Deploy: az deployment group create -g EsDAICoE-Sandbox -f main.bicep -p main.bicepparam

@description('Existing Cosmos DB account name in EsDAICoE-Sandbox')
param cosmosAccountName string = 'marco-cosmos'

@description('Existing Key Vault name')
param keyVaultName string = 'marco-kv'

@description('Database name for 51-ACA')
param databaseName string = 'aca-db'

var containers = [
  { name: 'scans',               partitionKey: '/subscriptionId' }
  { name: 'inventories',         partitionKey: '/subscriptionId' }
  { name: 'cost-data',           partitionKey: '/subscriptionId' }
  { name: 'advisor',             partitionKey: '/subscriptionId' }
  { name: 'findings',            partitionKey: '/subscriptionId' }
  { name: 'clients',             partitionKey: '/subscriptionId' }
  { name: 'deliverables',        partitionKey: '/subscriptionId' }
  { name: 'entitlements',        partitionKey: '/subscriptionId' }
  { name: 'payments',            partitionKey: '/subscriptionId' }
  { name: 'stripe_customer_map', partitionKey: '/stripeCustomerId' }
  { name: 'admin_audit_events',  partitionKey: '/subscriptionId' }  // admin ops audit trail
]

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' existing = {
  name: cosmosAccountName
}

resource acaDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmos
  name: databaseName
  properties: {
    resource: { id: databaseName }
  }
}

resource cosmosContainers 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = [
  for c in containers: {
    parent: acaDb
    name: c.name
    properties: {
      resource: {
        id: c.name
        partitionKey: {
          paths: [c.partitionKey]
          kind: 'Hash'
        }
        defaultTtl: -1
      }
    }
  }
]
