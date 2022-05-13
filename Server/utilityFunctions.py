from secrets import token_urlsafe
from hashlib import sha1

from json import dumps, loads

def getNewToken():
  token = sha1(token_urlsafe(100).encode()).hexdigest()[:2]
  return token, int(token, 16)

# def encodeMessage(message):
#   return [str(part).encode('utf-8') for part in message]

# def decodeMessage(message):
#   return [part.decode('utf-8') for part in message]

def encodeMessage(message):
    return [dumps(part).encode('utf-8') for part in message]

def decodeMessage(message):
    return [loads(part.decode('utf-8')) for part in message]

def getListFromStr(lstr):
  lst = lstr.replace('[','').replace(']','').replace(' ','').split(',')
  lst = [int(element) for element in lst]
  return lst