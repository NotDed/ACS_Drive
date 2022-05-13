
from sys import argv
import zmq
import os

import json

from utilityFunctions import getNewToken, encodeMessage, decodeMessage, getListFromStr

downloadSpeed = 1024**2 #1 megaByte

magnitude = 2**160

noneLimits = [-1,-1]
    
class SVDrive():
    
    def __init__(self, ip, port, tk = None):
        #token en hexa y decimal
        if not tk:
            self.token, self.intToken = getNewToken()
        else:
            self.token = tk
            self.intToken = int(tk)
        # self.token, self.intToken = getNewToken()
        self.ip = ip
        self.port = port
        
        #ip lista circular
        self.ipPort = 'tcp://{}:{}'.format(ip, port)
        self.nextIp = self.ipPort
        
        #rangos
        self.preRange = range(0, self.intToken)
        self.posRange = range(self.intToken, magnitude)
        
        #sockets
        self.context = zmq.Context()
        self.escucha = self.context.socket(zmq.REP)
        self.escucha.bind('tcp://*:{}'.format(port))
        self.pregunta = self.context.socket(zmq.REQ)
        
    def getServerInfo(self, opt = None):
        info = []
        if opt:
            info.append(opt)
            
        info.append(self.token)
        info.append(self.intToken)
        info.append(self.ipPort)
        info.append(self.nextIp)
        
        return info
        
    def setNextIp(self, newIp):
        self.nextIp = newIp
        
    def setPreRange(self, limits):
        if limits != noneLimits:
            self.preRange = range(limits[0], limits[1])
        else:
            self.preRange = None
        
    def setPosRange(self, limits):
        if limits != noneLimits:
            self.posRange = range(limits[0], limits[1])
        else:
            self.posRange = None
            
    def tokenInPreRange(self, token):
        result = False
        if self.preRange is not None and token in self.preRange:
            result = True
        return result
    
    def tokenInPosRange(self, token):
        result = False
        if self.posRange is not None and token in self.posRange:
            result = True
        return result
            
    def redefineServer(self, newParams):
        self.nextIp = newParams[0]
        self.token = newParams[1]
        # self.intToken = int(newParams[2])
        self.intToken = newParams[2]
        # self.setPreRange(getListFromStr(newParams[3]))
        # self.setPosRange(getListFromStr(newParams[4]))
        self.setPreRange(newParams[3])
        self.setPosRange(newParams[4])
        
    #asking next
        
    def sendMessageTo(self, ip, encodedMessage):
        self.pregunta.connect(ip)
        self.pregunta.send_multipart(encodedMessage)
        encodedResponse = self.pregunta.recv_multipart()
        self.pregunta.disconnect(ip)
        return encodedResponse
    
    def sendMessageToNext(self, encodedMessage):
        encodedResponse = self.sendMessageTo(self.nextIp, encodedMessage)
        return encodedResponse
    
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
    
    def attachToRing(self, ringIp):
        actualIp = ringIp
        attached = False
        
        self.setPreRange(noneLimits)
        self.setPosRange(noneLimits)
        
        message = self.getServerInfo('attach')
        message = encodeMessage(message)
                
        while not attached:
            response = self.sendMessageTo(actualIp, message)
            response = decodeMessage(response)
            
            if response[0] == 'accepted':
                attached = True
                self.redefineServer(response[2:-1])
                if response[-1] == 'pre':
                    if self.nextIp != self.ipPort:
                        if not response[1]:
                            newMessage = ['lowPre', self.intToken]
                        else:
                            newMessage = ['ignore']
                            
                        newMessage = encodeMessage(newMessage)
                        response = self.sendMessageToNext(newMessage)
                        
                    
            else:
                actualIp = response[1]
                if actualIp == ringIp:
                    break
                
    def waitForActions(self):
        end = False
        while True:
            
            print(self.getServerInfo())
            print('--------------------------------------------------------------------------')
            
            message = self.escucha.recv_multipart()
            message = decodeMessage(message)
            
            accion = message[0]
            
            response = []
            
            if accion == 'shutDown':
                response.append('Server ended')
                end = True
            
            elif accion == 'lowPre':
                lowerLimit = message[1]
                self.setPreRange([lowerLimit, self.intToken])
                
                response.append('Lower limit changed')
                
            elif accion == 'walk':
                response.extend(self.getServerInfo())
                if self.preRange is not None:
                    response.append([self.preRange[0],self.preRange[-1]])
                else:
                    response.append([])
                    
                if self.posRange is not None:
                    response.append([self.posRange[0],self.posRange[-1]])
                else:
                    response.append([])
            
            elif accion == 'attach':
                token = message[1]
                intToken = message[2]
                ipPort = message[3]
                
                inPreRange = self.tokenInPreRange(intToken)
                inPosRange = self.tokenInPosRange(intToken)
                
                response = []
                
                if inPreRange: #esta en el preRango
                    oneNodeRing = self.nextIp == self.ipPort
                    response.append('accepted')
                    response.append(oneNodeRing)
                    response.append(self.nextIp)
                    self.nextIp = ipPort
                    tempTk = self.token
                    tempIntTk = self.intToken
                    self.token = token
                    self.intToken = intToken
                    response.append(tempTk)
                    response.append(tempIntTk)
                    self.preRange = range(self.preRange[0], self.intToken)
                    self.posRange = None
                    response.append([self.intToken, tempIntTk])
                    
                    if oneNodeRing:
                        response.append([tempIntTk, magnitude])
                    else:
                        response.append(noneLimits)
                    
                    response.append('pre')
                    
                    #transferencia de datos
                    
                elif inPosRange:
                    response.append('accepted')
                    response.append(None)
                    response.append(self.nextIp)
                    
                    self.nextIp = ipPort
                    
                    response.append(token)
                    response.append(intToken)
                    
                    self.setPosRange(noneLimits)
                    
                    response.append([self.preRange[-1], intToken])
                    response.append([intToken,magnitude])
                    response.append('pos')
                    
                    #transferencia de datos
                else:
                    response.append('rejected')
                    response.append(self.nextIp)
                    
                    
            elif accion == 'info':
                response = self.getServerInfo()
                
            else:
                response.append('ok')
            
            response = encodeMessage(response)
            self.escucha.send_multipart(response)
            
            if end:
                break
                
ip = argv[1]
port  = argv[2]
accion = argv[3]

sv = SVDrive(ip, port)
print('--------------------------------------------------------------------------')
print(sv.getServerInfo())
print('--------------------------------------------------------------------------')

if accion == 'wa':
    sv.waitForActions()
elif accion == 'w':
    sv.walkRing(argv[4])
else:
    sv.attachToRing(accion)  
    sv.waitForActions()