import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient 

### Get Gov Data ###
import requests
import json

# We are using viennese metro lines data. For now, we use a API that makes data import easier. 
# https://www.data.gv.at/katalog/dataset/wiener-linien-echtzeitdaten-via-datendrehscheibe-wien
res = requests.get('http://vtapi.floscodes.net/?line=U4&station=Karlsplatz&towards=Heiligenstadt')

if res:
    print('Success!')
    resJSON = res.json()
    print(resJSON)
else:
    print('An error has occurred.')

overview = resJSON['data']['monitors'][0]["lines"][0] # needed data can be extracted from here. 

# # DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
# # It attempts to use multiple credential types in an order until it finds a working credential.

# # - AZURE_URL: The URL to the ADT in Azure
# url = os.getenv("https://BITWISEinstance.api.weu.digitaltwins.azure.net")

# # DefaultAzureCredential expects the following three environment variables:
# # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
# # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant CLIENT = APPLICATION
# # - AZURE_CLIENT_SECRET: The client secret for the registered application

# # AZURE_TENANT_ID = "0504f721-d451-402b-b884-381428559e39" # (is that the correct one?)
# # AZURE_CLIENT_ID = ???
# # AZURE_CLIENT_SECRET = ???
# # AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

# credential = DefaultAzureCredential()
# service_client = DigitalTwinsClient(url, credential) # ERROR -> "url" is type "None"

# component_id = "component001"
# model_id = "model001"

# temporary_component = {
#     "@id": component_id,
#     "@type": "Interface",
#     "@context": "dtmi:dtdl:context;2",
#     "displayName": "Component1",
#     "contents": [
#     {
#         "@type": "Property",
#         "name": "ComponentProp1",
#         "schema": "string"
#     },
#     {
#         "@type": "Telemetry",
#         "name": "ComponentTelemetry1",
#         "schema": "integer"
#     }
#     ]
# }

# temporary_model = {
#     "@id": model_id,
#     "@type": "Interface",
#     "@context": "dtmi:dtdl:context;2",
#     "displayName": "TempModel",
#     "contents": [
#     {
#         "@type": "Property",
#         "name": "Prop1",
#         "schema": "string"
#     },
#     {
#         "@type": "Component",
#         "name": "Component1",
#         "schema": component_id
#     },
#     {
#         "@type": "Telemetry",
#         "name": "Telemetry1",
#         "schema": "integer"
#     }
#     ]
# }

# new_models = [temporary_component, temporary_model]
# models = service_client.create_models(new_models)
# print('Created Models:')
# print(models)

