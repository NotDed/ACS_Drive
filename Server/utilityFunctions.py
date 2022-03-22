import os

def getPaths(mainDir, id, fileName):
    dirPath = '{}/{}'.format(mainDir, id)
    filePath = '{}/{}/{}'.format(mainDir, id, fileName)
    return (dirPath, filePath)

def decodeMessage(message):
    return (val.decode("utf-8") for val in message[:3]) #accion, id, fileName

def decodeParams(message):
    messageSlice = message[3:]
    if len(messageSlice) > 1:
        return (messageSlice[0].decode("utf-8"), messageSlice[1])
    else:
        return int(messageSlice[0].decode('utf-8'))
    
def makeOrVerify(dirPath, make=False):
    if not os.path.exists(dirPath):
        if make:
            os.makedirs(dirPath)
        return False
    return True