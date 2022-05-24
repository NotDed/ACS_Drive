
from base64 import decode, encode
from sys import argv
from numpy import False_
import zmq
import os

import json

from utilityFunctions import getNewToken, encodeMessage, decodeMessage

# downloadSpeed = (1024**2)*10 #10 megabytes

magnitude = 2**160

noneLimits = [-1,-1]
    
class SVDrive():
    
    def __init__(self, ip, port, tk = None):
        self.ipPort = 'tcp://{}:{}'.format(ip, port)
        self.nextIp = self.ipPort
        
        self.storageDir = 'storage/{}({})'.format(ip, port)
        
        self.token, self.intToken = getNewToken(tk)
        
        self.preRange = []
        self.preRange.append(0)
        self.preRange.append(self.intToken)
        
        self.posRange = []
        self.posRange.append(self.intToken)
        self.posRange.append(magnitude)
    
        #sockets
        self.context = zmq.Context()
        self.escucha = self.context.socket(zmq.REP)
        self.escucha.bind('tcp://*:{}'.format(port))
        self.pregunta = self.context.socket(zmq.REQ)
        
    def makeStorageDir(self):
        if not os.path.exists(self.storageDir):
            os.makedirs(self.storageDir)
            
    def getFilesInServer(self):
        return os.listdir(self.storageDir)
    
    def getFilesNotInRange(self):
        notInServer = []
        inServer = self.getFilesInServer()
        
        for intToken in inServer:
            intToken = int(intToken)
            
            inPreRange = self.tokenInRange(intToken, self.preRange)
            inPosRange = self.tokenInRange(intToken, self.posRange)
            
            if not (inPreRange or inPosRange):
                notInServer.append(str(intToken))
            
        return notInServer
    
    def getServerInfo(self, opt = None):
        info = []
        if opt:
            info.append(opt)
        info.append(self.token)
        info.append(self.intToken)
        info.append(self.ipPort)
        info.append(self.nextIp)
        info.append(self.preRange)
        info.append(self.posRange)
        return info
    
    def setPreRange(self, limits):
        self.preRange = limits if limits != noneLimits else None
            
    def setPosRange(self, limits):
        self.posRange = limits if limits != noneLimits else None
    
    def tokenInRange(self, token, limits):
        return limits is not None and token >= limits[0] and token < limits[1]
    
    def redefineServer(self, newParams):
        self.nextIp = newParams[0]
        self.token = newParams[1]
        self.intToken = newParams[2]
        self.preRange = newParams[3]
        self.posRange = newParams[4]
        
    def sendMessageTo(self, ip, message):
        self.pregunta.connect(ip)
        self.pregunta.send_multipart(message)
        response = self.pregunta.recv_multipart()
        self.pregunta.disconnect(ip)
        return response
    
    def sendMessageToNext(self, message):
        return self.sendMessageTo(self.nextIp, message)
    
    def waitMessage(self):
        message = self.escucha.recv_multipart()
        accion = json.loads(message[0].decode('utf-8'))
        return accion, message
    
    def walkRing(self, ringIp):
        actualIp = ringIp
        message = ['walk']
        message = encodeMessage(message)
        
        while True:
            
            response = self.sendMessageTo(actualIp, message)
            response = decodeMessage(response)
            
            print('{} : {} -> {}: {} U {}'.format(response[1], response[2], response[3], response[4], response[5]))
            
            actualIp = response[3]
            
            if actualIp == ringIp:
                break
            
    def endServer(self):
        response = ['Server ended', self.nextIp]
        end = True
        return response, end
    
    def attachToRing(self, ringIp):
        attached = False
        actualIp = ringIp
        
        message = self.getServerInfo('attach')
        message = encodeMessage(message)
        
        while not attached:
            response = self.sendMessageTo(actualIp, message)
            response = decodeMessage(response)
            
            if response[0] == 'accepted':
                attached = True
                self.redefineServer(response[1])
                
            else:
                actualIp = response[1]
                if actualIp == ringIp:
                    break
                
    def attachNewServer(self, encodedMessage):
        message = decodeMessage(encodedMessage)
        response = []
        token = message[1]
        intToken = message[2]
        ipPort = message[3]
        
        inPreRange = self.tokenInRange(intToken, self.preRange)
        inPosRange = self.tokenInRange(intToken, self.posRange)
        
        if inPreRange or inPosRange:
            response.append('accepted')
            info = []
            info.append(self.nextIp)
            self.nextIp = ipPort
            if inPreRange: #en pre rango
                info.append(self.token)
                info.append(self.intToken)
                info.append([intToken, self.preRange[1]])
                if self.posRange is not None:
                    info.append([self.intToken, self.posRange[1]])
                else:
                    info.append(None)
                self.token = token
                self.intToken = intToken
                self.preRange[1] = self.intToken
            elif inPosRange: #en pos rango
                info.append(token)
                info.append(intToken)
                info.append([self.intToken, intToken])
                info.append([intToken, magnitude])
            response.append(info)
                
            self.posRange = None 
        else:
            response.append('rejected')
            response.append(self.nextIp)
            
        return response

    def verifyArchives(self):
        notInServer = self.getFilesNotInRange()
        actualIp = self.nextIp
        for intToken in notInServer:
            accepted = False
            filePath = '{}/{}'.format(self.storageDir, intToken)
            
            message = []
            message.append('upload')
            message.append(intToken)
            message = encodeMessage(message)
            
            with open(filePath, 'rb') as f:
                part = f.read()
            
            message.append(part) 
            while not accepted:
                response = self.sendMessageTo(actualIp, message)
                response = decodeMessage(response)
                if response[0] == 'accepted':
                    accepted = True
                    os.remove(filePath)
                else:
                    actualIp = response[1]
    
    def walkThroughThis(self):
        response = []
        response.extend(self.getServerInfo())
        if self.preRange is not None:
            response.append([self.preRange[0],self.preRange[-1]])
        else:
            response.append([])
            
        if self.posRange is not None:
            response.append([self.posRange[0],self.posRange[-1]])
        else:
            response.append([])
            
        return response
    
    def upload(self, message):
        filePart = message[-1]
        decodedMessage = decodeMessage(message[:-1])
        intToken = int(decodedMessage[1])
        
        filePath = '{}/{}'.format(self.storageDir, intToken)
        
        inPreRange = self.tokenInRange(intToken, self.preRange)
        inPosRange = self.tokenInRange(intToken, self.posRange)
        
        response = []
        if inPreRange or inPosRange:
            print('subiendo: ', intToken)
            with open(filePath, 'wb') as f:
                f.write(filePart)
            response.append('accepted')
        else:
            response.append('rejected')
            response.append(self.nextIp)
            
        return response
    
    def download(self, message):
        message = decodeMessage(message)
        intToken = int(message[1])
        

        inPreRange = self.tokenInRange(intToken, self.preRange)
        inPosRange = self.tokenInRange(intToken, self.posRange)
        serverFiles = self.getFilesInServer()
        
        response = []
        
        if (inPreRange or inPosRange) and str(intToken) in serverFiles:
            response.append('accepted')
            response = encodeMessage(response)
            filePath = '{}/{}'.format(self.storageDir, intToken)
            with open(filePath, 'rb') as f:
                response.append(f.read())
                
        else:
            response.append('rejected')
            response.append(self.nextIp)
            response = encodeMessage(response)
            
        return response
    
    def decodeResponse(self, accion, response):
        encodedResponse = response
        if accion != 'download':
            encodedResponse = encodeMessage(encodedResponse)
        return encodedResponse
    
    def waitForActions(self):
        end = False
        while not end:
            self.verifyArchives()
            print(self.getServerInfo())
            accion, message = self.waitMessage()
            response = []
            if accion == 'shutDown':
                response, end = self.endServer()
                
            elif accion == 'info':
                response = self.getServerInfo()
                
            elif accion == 'attach':
                response = self.attachNewServer(message)
                    
            elif accion == 'walk':
                response = self.walkThroughThis()
                
            elif accion == 'upload':
                response = self.upload(message)
                
            elif accion == 'download':
                response = self.download(message)
                
            else:
                response.append('error')
                
            response = self.decodeResponse(accion, response)
            self.escucha.send_multipart(response)
            


puerto = argv[1]
accion = argv[2]

sv = SVDrive('localhost', puerto)

if accion == 'waitActions':
    sv.makeStorageDir()
    sv.waitForActions()
if accion == 'walk':
    ip = argv[3]
    sv.walkRing(ip)
if accion == 'attach':
    ip = argv[3]
    sv.makeStorageDir()
    sv.attachToRing(ip)
    sv.waitForActions()