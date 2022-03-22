import json
import os

def verifyConfig():
    return os.path.exists('config.json')

def updateJSON(jsonName, data):
    with open(jsonName, 'w+') as f:
        json.dump(data, f, indent=4)
        
def loadJSON(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data