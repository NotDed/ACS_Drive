import zmq
import os

from utilityFunctions import getPartitions

class PROXDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REP)
        self.s.bind('tcp://*:8001')
        
        self.servers = {}
        self.filePartitions = {}
        
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
                self.uploadLogistic(id, fileName, partCount)
        
        
proxy = PROXDrive()
proxy.waitForActions()
        