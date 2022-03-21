import zmq
import os

downloadSpeed = 8

mainDir = 'Data'

class SVDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REP)
        self.s.bind('tcp://*:8001')
        
    def waitForActions(self):
        while True:
            message = self.s.recv_multipart()
            
            accion = message[0].decode('utf-8') #accion
            id = message[1].decode('utf-8') #identificador de usuario
            fileName = message[2].decode('utf-8') #nombre del archivo
            
            dirPath = '{}/{}'.format(mainDir, id)
            filePath = '{}/{}/{}'.format(mainDir, id, fileName)
            
            if accion == 'u':
                modo = message[3].decode('utf-8') #modo de escritura
                data = message[4] #data
                
                print('{} is uploading on file {}'.format(id, fileName))
                
                if not os.path.exists(dirPath):
                    os.makedirs(dirPath)
                    
                
                with open(filePath, modo) as f:
                    f.write(data)
                    
                self.s.send_multipart(['exito'.encode('utf-8'), dirPath.encode('utf-8')])
                
            elif accion == 'd':
                response = []
                pointerState = int(message[3].decode('utf-8'))
                
                print('{} is downloading on file {}'.format(id, fileName))
                
                with open(filePath, 'rb') as f:
                    f.seek(pointerState * downloadSpeed)
                    data = f.read(downloadSpeed)
                    
                pointerState += 1
                pointerState = str(pointerState).encode('utf-8') 
                
                response.append(pointerState)
                response.append(data)
                
                self.s.send_multipart(response)
                    
                    
                
        

BBSV = SVDrive()
BBSV.waitForActions()