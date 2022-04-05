from sys import argv
import zmq
import os

from utilityFunctions import decodeMessage, decodeParams, getPaths, makeOrVerify

downloadSpeed = 1024 #1 kiloByte
# downloadSpeed = 1024**2 #1 megaByte

class SVDrive():
    
    def __init__(self, ip, port, capacity):
        self.mainDir = '{}({})/Data'.format(ip, port)
        self.ip = 'tcp://{}:{}'.format(ip, port)
        self.capacity = capacity
        
        self.links = {}
        
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REP)
        self.s.bind('tcp://*:{}'.format(port))
        self.proxySocket = self.context.socket(zmq.REQ)
        
    def notifyProxy(self):
        self.proxySocket.connect('tcp://localhost:8001')
        message = {}
        message['accion'] = 'asv'
        message['ip'] = self.ip
        message['storage'] = self.capacity
        self.proxySocket.send_json(message)
        self.proxySocket.recv_json()

    def getFileUploads(self, message, dirPath, filePath):
        response = []
        
        modo, data = decodeParams(message)
        
        makeOrVerify(dirPath, make=True)
        
        with open(filePath, modo) as f:
            f.write(data)
            
        response.append('exito'.encode('utf-8'))
        response.append(dirPath.encode('utf-8'))
            
        self.s.send_multipart(response)
        

    def setFileDownloads(self, message, filePath):
        response = []
        pointerState = decodeParams(message)
        
        if makeOrVerify(filePath):
            with open(filePath, 'rb') as f:
                f.seek(pointerState * downloadSpeed)
                data = f.read(downloadSpeed)
                
            pointerState += 1
            pointerState = str(pointerState).encode('utf-8')
            
            response.append(pointerState)
            response.append(data)
        else:
            response.append('error'.encode('utf-8'))
            response.append('el directorio no se encontró'.encode('utf-8'))
            
        self.s.send_multipart(response)
        
    def setFileDownloadsByLink(self, message, filePath, fileName):
        response = []
        pointerState = decodeParams(message)
        
        if makeOrVerify(filePath):
            with open(filePath, 'rb') as f:
                f.seek(pointerState * downloadSpeed)
                data = f.read(downloadSpeed)
                
            pointerState += 1
            pointerState = str(pointerState).encode('utf-8')
            
            response.append(pointerState)
            response.append(data)
            response.append(fileName.encode('utf-8'))
        else:
            response.append('error'.encode('utf-8'))
            response.append('el directorio no se encontró'.encode('utf-8'))
            
        self.s.send_multipart(response)
        
    def addLink(self, message):
        decoded = [i.decode('utf-8') for i in message]
        url = decoded[1]
        fileLogisticId = tuple(decoded[2:4])
        self.links[url] = fileLogisticId
        
        response = []
        response.append('exito'.encode('utf-8'))
        response.append('todo gud'.encode('utf-8'))
        
        self.s.send_multipart(response)
        
    def waitForActions(self):
        while True:
            
            # print(self.links)
            message = self.s.recv_multipart()
            
            accion = message[0].decode('utf-8')
            
            if accion in ['u', 'd']:
                id, fileName = decodeMessage(message)
                dirPath, filePath = getPaths(self.mainDir, id, fileName)
                
                if accion == 'u':
                    print('{} is uploading on file {}'.format(id, fileName))
                    self.getFileUploads(message, dirPath, filePath)
                    
                elif accion == 'd':
                    print('{} is downloading on file {}'.format(id, fileName))
                    self.setFileDownloads(message, filePath)
            else:
                if accion == 'dl': #download with link
                    link = message[1].decode('utf-8')
                    id, fileName = self.links[link]
                    _, filePath = getPaths(self.mainDir, id, fileName)
                    self.setFileDownloadsByLink(message, filePath, fileName)
                    
                elif accion == 'al': #add link
                    self.addLink(message)
                    
                
        

ip = argv[1]
port = argv[2]
capacity = int(argv[3])

BBSV = SVDrive(ip, port, capacity)
BBSV.notifyProxy()
BBSV.waitForActions()