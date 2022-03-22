
import zmq
import json
from  hashlib import sha1
import secrets

from sys import argv

from utilityFunctions import updateJSON, loadJSON, verifyConfig

uploadSpeed = 1024**2

class CLDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.s = self.context.socket(zmq.REQ)
        
    def createConfig(self, user):
        identifier = '{}{}'.format(user, secrets.token_urlsafe(16)).encode('utf-8')
        identifier = sha1(identifier).hexdigest()
        config = {
            "user": user,
            "identifier":identifier,
        }
        self.config = config
        updateJSON('config.json', config)
            
    def loadConfig(self):
        self.config = loadJSON('config.json')
            
    def upload(self, fileName):
        self.s.connect('tcp://localhost:8001')
        self.loadConfig()
        
        id = self.config['identifier'].encode('utf-8')
        accion = 'u'.encode('utf-8')
        
        
        with open(fileName, 'rb') as f:
            while True:
                message = []
                modo = 'wb' if f.tell() == 0 else 'ab'
                modo = modo.encode('utf-8')
                
                data = f.read(uploadSpeed)
                
                if not data:
                    break
                
                message.append(accion) #accion
                message.append(id) #identificador de usuario
                message.append(fileName.encode('utf-8')) #nombre del archivo
                message.append(modo) #estado
                message.append(data) #data
                self.s.send_multipart(message)
                self.s.recv_multipart()
                
                
    def download(self, fileName):
        self.s.connect('tcp://localhost:8001')
        self.loadConfig()
        
        id = self.config['identifier'].encode('utf-8')
        accion = 'd'.encode('utf-8')
        pointerState = '0'.encode('utf-8')
        
        while True:
            message = []
            modo = 'wb' if pointerState == 0 else 'ab'
            
            message.append(accion) #accion
            message.append(id) #identificador de usuario
            message.append(fileName.encode('utf-8')) #nombre del archivo
            message.append(pointerState) #estado del puntero
            
            self.s.send_multipart(message)
            
            response = self.s.recv_multipart()
            
            if response[0].decode('utf-8') == 'error':
                print(response[1].decode('utf-8'))
                break
            
            pointerState = response[0]
            data = response[1]
            
            if not data:
                break
            
            with open(fileName, modo) as f:
                f.write(data)
        
 
Client = CLDrive()
if verifyConfig():
    if argv[1] == 'u':
        Client.upload(argv[2])
    elif argv[1] == 'd':
        Client.download(argv[2])
        
else:
    print('''
          Este cliente aun no
          tiene configuracion inicial
          por favor ingrese su nombre
          de usuario: ''')
    user = input('          ')
    Client.createConfig(user)