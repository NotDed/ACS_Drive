import zmq
import os

from utilityFunctions import decodeMessage, decodeParams, getPaths, makeOrVerify

downloadSpeed = 1024**2

mainDir = 'Data'

class SVDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REP)
        self.s.bind('tcp://*:8001')

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
        
    def waitForActions(self):
        while True:
            message = self.s.recv_multipart()
            
            accion, id, fileName = decodeMessage(message)
            dirPath, filePath = getPaths(mainDir, id, fileName)
            
            if accion == 'u':
                print('{} is uploading on file {}'.format(id, fileName))
                self.getFileUploads(message, dirPath, filePath)
                
            elif accion == 'd':
                print('{} is downloading on file {}'.format(id, fileName))
                self.setFileDownloads(message, filePath)
                    
                
        

BBSV = SVDrive()
BBSV.waitForActions()