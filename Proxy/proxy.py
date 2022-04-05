import zmq
import os

from utilityFunctions import getPartitions
from secrets import token_urlsafe

class PROXDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REP)
        self.s.bind('tcp://*:8001')
        
        self.serverConn = self.context.socket(zmq.REQ)
        
        self.servers = {}
        self.filePartitions = {}
        self.links = {}
        
        
    def addServer(self, ip, storage):
        if not ip in self.servers.keys():
            self.servers[ip] = storage
            response = ['exito']
        else:
            response = ['error']
        
        self.s.send_json(response)
        
       
    def uploadLogistic(self, id, fileName, partCount):
        fileLogisticId = '{}{}'.format(id, fileName)
        partitions = getPartitions(self.servers, partCount)
        
        if len(partitions) > 0:
            self.filePartitions[fileLogisticId] = partitions
            response = ['exito', partitions]
        else:
            response = ['error', 'algo salio mal']
            
        self.s.send_json(response)
            
            
    def downloadLogistic(self, id, fileName):
        fileLogisticId = '{}{}'.format(id, fileName)
        
        if fileLogisticId in self.filePartitions.keys():
            partitions = self.filePartitions[fileLogisticId]
            response = ['exito', partitions]
        else:
            response = ['error', 'algo salio mal']
            
        self.s.send_json(response)
        
    def generateLink(self, id, fileName):
        fileLogisticId = '{}{}'.format(id, fileName)
        newUrl = token_urlsafe(16)
        
        print(fileLogisticId)
        
        if fileLogisticId in self.filePartitions.keys():
            self.links[newUrl] = (id, fileName)
            response = ['exito', newUrl]
        else:
            response = ['error', 'algo salio mal']
            
        self.s.send_json(response)
        if response[0] == 'exito':
            self.broadCastToServers([newUrl, id, fileName])
        
    def broadCastToServers(self, urlPacket):
        message = ['al']
        message.extend(urlPacket)
        message = [i.encode('utf8') for i in message]
        for ip in self.servers.keys():
            self.serverConn.connect(ip)
            self.serverConn.send_multipart(message)
            response = self.serverConn.recv_multipart()
            self.serverConn.disconnect(ip)
        
    def waitForActions(self):
        while True:
            print(self.servers)
            print(self.filePartitions)
            message = self.s.recv_json()
            
            accion = message['accion']
            
            if accion == 'asv':
                ip = message['ip']
                storage = message['storage']
                self.addServer(ip, storage)
            
            if accion == 'u':
                id = message['id']
                fileName = message['fileName']
                partCount = message['partCount']
                self.uploadLogistic(id, fileName, partCount)
                
            if accion == 'd':
                id = message['id']
                fileName = message['fileName']
                self.downloadLogistic(id, fileName)
                
            if accion == 'gl':
                id = message['id']
                fileName = message['fileName']
                self.generateLink(id, fileName)
                
            elif accion == 'dl':
                url = message['link']
                id, filename = self.links[url]
                self.downloadLogistic(id, fileName)
                
                
                
        
        
proxy = PROXDrive()
proxy.waitForActions()
        