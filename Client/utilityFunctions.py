import json
import os

from math import ceil

def requiredParts(path, partSize = 1024):
  with open(path, 'rb')as f:
    f.seek(0,2)
    size = f.tell()
  return ceil(size/partSize)

def verifyConfig():
    return os.path.exists('config.json')

def updateJSON(jsonName, data):
    with open(jsonName, 'w+') as f:
        json.dump(data, f, indent=4)
        
def loadJSON(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data