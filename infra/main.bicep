targetScope = 'subscription'

param location string = 'westeurope'
param resourceGroupName string
param acrName string
param sku string = 'Basic'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
}

module acr 'acr.bicep' = {
  name: 'acrDeploy'
  scope: rg
  params: {
    acrName: acrName
    location: location
    sku: sku
  }
}
