import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient 
from dateutil.parser import parse
import hashlib
import pandas as pd
import requests
import json
import time
from datetime import datetime


# Hash Model
# filename = "patch.json"
# with open(filename, "rb") as f:
#     bytes = f.read() # read entire file as bytes
#     readable_hash = hashlib.sha256(bytes).hexdigest();
#     print(readable_hash)


###### API Connection & Data Extraction #######

# We are using viennese metro lines data. For now, we use a API that makes data import easier. 
# https://www.data.gv.at/katalog/dataset/wiener-linien-echtzeitdaten-via-datendrehscheibe-wien
lineName = "U3"
trainDirections = ["Simmering", "Ottakring"]
stationSchw = "Landstraße"
stationStep = "Stephansplatz"
# res = requests.get(f'http://vtapi.floscodes.net/?line={lineName}&station={stationName}&towards={trainDirecton}')

use_saved_data = True
if use_saved_data is True:
    SchwRdif = 0
    StepRdif = 0
    SchwHdif = 0
    StepHdif = 0
else:
    for trainIdx, trainDirection in enumerate(trainDirections):
        if trainIdx != 0:
            print("Wait 15s for Fair Use of API.")
            time.sleep(15)

        print(f"Get data towards {trainDirection}.")
        res = requests.get(f'http://vtapi.floscodes.net/?line={lineName}&towards={trainDirection}')

        if res:
            print('API: Success!')
            resJSON = res.json()
        else:
            print('An API error has occurred.')    

        # We extract following data:
        # Station "Stephansplatz" and "Schwedenplatz" as they are next to each other and have two lines 
        # We are focusing on line "U1". Thus, the directions are towards "Leopoldau" and "Oberlaa". 
        # For both directions, we get the next departureTimePlanned and Real

        monitors = resJSON['data']['monitors']

        # Check Stationnames Number
        stationNames = []
        for x in monitors:
            stationNames.append(x["locationStop"]["properties"]["title"])

        # Check whether wanted station names exist
        # if any(stationStep in sl["locationStop"]["properties"]["title"] for sl in monitors) == True and any(stationSchw in sl["locationStop"]["properties"]["title"] for sl in monitors) == False:
        if all(sl in stationNames for sl in [stationSchw, stationStep]) == False:
            print("One of the stations didn't exist.")
            print(f"Error in Direction: {trainDirection}")
            print("Wait 15s for Fair Use.")
            time.sleep(15)
            exit()

        # Get idx of selected stations
        for idx, m in enumerate(monitors):
            if m["locationStop"]["properties"]["title"] == stationStep:
                idxStep = idx
            if m["locationStop"]["properties"]["title"] == stationSchw:
                idxSchw = idx

        # Get the time data from the stations
        if trainDirection == trainDirections[0]: # Oberlaa
            monitorStep = monitors[idxStep]  # 14 - Stephansplatz
            monitorSchw = monitors[idxSchw]  # 0 - Schwedenplatz
            SchwRplan = monitorSchw["lines"][0]['departures']['departure'][0]['departureTime']['timePlanned']
            SchwRreal = monitorSchw["lines"][0]['departures']['departure'][0]['departureTime']['timeReal']
            SchwRdif = (parse(SchwRreal) - parse(SchwRplan)).seconds
            StepRplan = monitorStep["lines"][0]['departures']['departure'][0]['departureTime']['timePlanned']
            StepRreal = monitorStep["lines"][0]['departures']['departure'][0]['departureTime']['timeReal']
            StepRdif = (parse(StepRreal) - parse(StepRplan)).seconds
        else:
            monitorStep = monitors[idxStep]  # 43 - Stephansplatz
            monitorSchw = monitors[idxSchw]  # 33 - Schwedenplatz
            SchwHplan = monitorSchw["lines"][0]['departures']['departure'][0]['departureTime']['timePlanned']
            SchwHreal = monitorSchw["lines"][0]['departures']['departure'][0]['departureTime']['timeReal']
            SchwHdif = (parse(SchwHreal) - parse(SchwHplan)).seconds
            StepHplan = monitorStep["lines"][0]['departures']['departure'][0]['departureTime']['timePlanned']
            StepHreal = monitorStep["lines"][0]['departures']['departure'][0]['departureTime']['timeReal']
            StepHdif = (parse(StepHreal) - parse(StepHplan)).seconds




###### AZURE #######

# Connection and Authenticaiton to Azure

# - AZURE_URL: The URL to the ADT in Azure
print("Start AZURE")
url = "https://BITWISEinstance.api.weu.digitaltwins.azure.net"
credential = DefaultAzureCredential()
service_client = DigitalTwinsClient(url, credential) 


# Check for models
listed_models = service_client.list_models()
for model in listed_models:
    print(model)


# Create model and Components

### Network + Station 1 + Station 2
network_id = "dtmi:Network;1"
station1_id = "dtmi:Station;1"
station2_id = "dtmi:Station;2"
context_model = "dtmi:dtdl:context;2"
component_id = "dtmi:Component;1"


temporary_component = {
    "@id": component_id,
    "@type": "Interface",
    "@context": context_model,
    "displayName": "Component1",
    "contents": [
    {
        "@type": "Property",
        "name": "network_name",
        "schema": "string"
    }
    ]
}

network_model = {
    "@id": network_id,
    "@type": "Interface",
    "displayName": "Transport Network",
    "@context": context_model,
    "contents": [
      {
          "@type": "Property",
          "name": "U_Bahn_Network_name",
          "schema": "string"
        },
      {
        "@type": "Relationship",
        "name": "contains",
        "displayName": "contains",
        "target": station1_id
      },
      {
        "@type": "Relationship",
        "name": "contains",
        "displayName": "contains",
        "target": station2_id
      },
      {
        "@type": "Component",
        "name": "Component1",
        "schema": component_id
      }
        ]
    }, {
    "@id": station1_id,
    "@type": "Interface",
    "@context": context_model,
    "displayName": "Station1",
    "contents": [
        {
          "@type": "Property",
          "name": "station1_name",
          "schema": "string"
        },
        {
            "@type": "Property",
            "name": "line_name",
            "schema": "string"
        },
        {
          "@type": "Property",
          "name": "time_of_measurement",
          "schema": "dateTime"
        },
        {
            "@type": "Property",
            "name": "S1Hdiff",
            "schema": "integer"
        },
        {
            "@type": "Property",
            "name": "S1Rdiff",
            "schema": "integer"
        }
        ]
        
    }, {
    "@id": station2_id,
    "@type": "Interface",
    "@context": context_model,
    "displayName": "Station2",
    "contents": [
        {
          "@type": "Property",
          "name": "station2_name",
          "schema": "string"
        },
        {
            "@type": "Property",
            "name": "line_name",
            "schema": "string"
        },
        {
          "@type": "Property",
          "name": "time_of_measurement",
          "schema": "dateTime"
        },
        {
            "@type": "Property",
            "name": "S2Hdiff",
            "schema": "integer"
        },
        {
            "@type": "Property",
            "name": "S2Rdiff",
            "schema": "integer"
        }
        ]
    }




# Set to True, if models are deleted. For a change, delete model in ADT Explorer. 
if False:
    new_models = [temporary_component, network_model]
    models = service_client.create_models(new_models)
    models2 = service_client.create_models(network_model)
    print('Created Models.')
    print("Models:")
    print(models)
    print(models2)



# Build Digital Twin (instance). Twin property must be consistent with model.  # setPointTemp
network_twin_id = "Network_twin"
station1_twin_id = "Stephansplatz_twin"
station2_twin_id = "Landstraße_twin"

temporary_network_twin = {
    "$metadata": {
        "$model": network_id
    },
    "$dtId": network_twin_id,
    "U_Bahn_Network_name": "Wiener Linien U-Bahnen", 
    "Component1": {
        "$metadata": {},
        "network_name": "network_name" 
    }
}
temporary_station1_twin = {
    "$metadata": {
        "$model": station1_id
    },
    "$dtId": station1_twin_id,
    "station1_name": "Stephansplatz",
    "line_name": lineName,
    "time_of_measurement": datetime.now(),
    "S1Hdiff": StepHdif,
    "S1Rdiff": StepRdif
}
temporary_station2_twin = {
    "$metadata": {
        "$model": station2_id
    },
    "$dtId": station2_twin_id,
    "station2_name": "Landstraße",
    "line_name": lineName,
    "time_of_measurement": datetime.now(),
    "S2Hdiff": SchwHdif,
    "S2Rdiff": SchwRdif
}


try:
    created_twin = service_client.upsert_digital_twin(network_twin_id, temporary_network_twin)
    created_twin = service_client.upsert_digital_twin(station1_twin_id, temporary_station1_twin)
    created_twin = service_client.upsert_digital_twin(station2_twin_id, temporary_station2_twin)
    print('Created Digital Twin:')
    print(created_twin)
except: 
    get_twin = service_client.get_digital_twin(network_twin_id)
    get_twin = service_client.get_digital_twin(station1_id)
    get_twin = service_client.get_digital_twin(station2_id)
    print('Get Digital Twin.')


# Query Twin to see that output changed
query_expression = 'SELECT * FROM digitaltwins'
query_result = service_client.query_twins(query_expression)
print('DigitalTwins:')
for twin in query_result:
    print(twin)




# update components of digital twin
# component_name = "Component1"
# # JSON schema to change variable within Component. -> See if DT has component in Twin model!
# patchComponent = [
#   {
#     "op": "replace",
#     "path": "/ComponentProp1",
#     "value": difference
#   }
# ]
# service_client.update_component(digital_twin_id, component_name, patchComponent)
# print(service_client.get_component(digital_twin_id, component_name))



# JSON Schema to change Variable directly. after that, query Twin again to see results!
patchStephansplatz = [
  {
    "op": "add",
    "path": "/S1Hdiff",
    "value": StepHdif
  },
  {
    "op": "add",
    "path": "/S1Rdiff",
    "value": StepRdif
  }
]
patchLandstraße = [
  {
    "op": "add",
    "path": "/S2Hdiff",
    "value": SchwHdif
  },
  {
    "op": "add",
    "path": "/S2Rdiff",
    "value": SchwRdif
  }
]

service_client.update_digital_twin(station1_twin_id, patchStephansplatz)
service_client.update_digital_twin(station2_twin_id, patchLandstraße)
# print(service_client.get_digital_twin(station1_id))


print("Program end.")

## Further Work
# - Concretisise and expand the model 
# - Upload Model to Blockchain with static data
# - visualisation of real-time changes in Data Explorer historically
