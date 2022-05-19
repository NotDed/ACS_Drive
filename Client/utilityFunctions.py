import json
import os

from math import ceil
from hashlib import sha1


uploadSpeed = 100#(1024**2)*10

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
  
def encodeMessage(message):
    return [json.dumps(part).encode('utf-8') for part in message]

def decodeMessage(message):
    return [json.loads(part.decode('utf-8')) for part in message]
  
def messageToUpload(hash, part):
  message = ['upload', hash]
  message = encodeMessage(message)
  message.append(part)
  return message

def getPartsAndHashes(fileName):
  messages = []
  partHashes = []
  completeFileHash = sha1()
  with open(fileName, 'rb') as f:
    while True:
      chunk = f.read(uploadSpeed)

      if not chunk:
        break
      #single part hashing
      partHash = sha1(chunk)
      partHash = partHash.hexdigest()
      partHash = int(partHash,16)
      partHashes.append(partHash)

      messages.append(messageToUpload(partHash, chunk))
      #complete file hashing
      completeFileHash.update(chunk)

  #complete file hashing to hexa
  completeFileHash = completeFileHash.hexdigest()

  torrentName = makeTorrent(fileName, completeFileHash, partHashes)
  return torrentName, messages
  
def makeTorrent(fileName, completeFileHash, partHashes):
  completeFileName = fileName.split('.')
  name = completeFileName[0]
  extension = completeFileName[1]

  torrent = {}
  torrent['fileName'] = name
  torrent['extension'] = extension
  torrent['completeFileHash'] = completeFileHash
  torrent['parts'] = partHashes
  
  torrentName = '{}.torrent'.format(name)
  updateJSON(torrentName, torrent)

  return torrentName