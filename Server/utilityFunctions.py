from secrets import token_urlsafe
from hashlib import sha1

from json import dumps, loads

def getNewToken(tk):
  if tk is None:
    token = sha1(token_urlsafe(100).encode()).hexdigest()
  else:
    token = tk
  return token, int(token, 16)

# def encodeMessage(message):
#   return [str(part).encode('utf-8') for part in message]

# def decodeMessage(message):
#   return [part.decode('utf-8') for part in message]

def encodeMessage(message):
    return [dumps(part).encode('utf-8') for part in message]

def decodeMessage(message):
    return [loads(part.decode('utf-8')) for part in message]