
import zmq
import json
from  hashlib import sha1
import secrets

from sys import argv

from utilityFunctions import updateJSON, loadJSON, verifyConfig, requiredParts

uploadSpeed = 1024 #1 kiloByte
# uploadSpeed = 1024**2 #1 megaByte

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
        
    def addServer(self, ip, storage):
        self.s.connect('tcp://localhost:8001')
        
        message = {}
        message['accion'] = 'asv'
        message['ip'] = ip
        message['storage'] = storage

        self.s.send_json(message)
        
        response = self.s.recv_json()
        
        print(response)
        
    def askToUpload(self, fileName):
        proxy = 'tcp://localhost:8001'
        self.s.connect(proxy)
        
        id = self.config['identifier']
        
        partCount = requiredParts(fileName)
        
        message = {}
        message['accion'] = 'u'
        message['id'] = id
        message['fileName'] = fileName
        message['partCount'] = partCount

        self.s.send_json(message)
        
        response = self.s.recv_json()
        
        self.s.disconnect(proxy)
        
        return response
        
    def askToDownload(self, fileName):
        proxy = 'tcp://localhost:8001'
        self.s.connect(proxy)
        
        id = self.config['identifier']
        
        message = {}
        message['accion'] = 'd'
        message['id'] = id
        message['fileName'] = fileName

        self.s.send_json(message)
        
        response = self.s.recv_json()
        self.s.disconnect(proxy)
        
        return response
    
    def askToDownloadLink(self, link):
        proxy = 'tcp://localhost:8001'
        self.s.connect(proxy)
        
        id = self.config['identifier']
        
        message = {}
        message['accion'] = 'dl'
        message['id'] = id
        message['link'] = link

        self.s.send_json(message)
        
        response = self.s.recv_json()
        self.s.disconnect(proxy)
        
        return response
    
    def askForLink(self, fileName):
        self.loadConfig()
        proxy = 'tcp://localhost:8001'
        self.s.connect(proxy)
        
        id = self.config['identifier']
        
        message = {}
        message['accion'] = 'gl'
        message['id'] = id
        message['fileName'] = fileName
        
        self.s.send_json(message)
        response = self.s.recv_json()
        
        print('the link for sharing {} is: \n\n {} \n'.format(fileName, response[1]))
        
        
    def upload(self, fileName):
        self.loadConfig()
        
        partitions = self.askToUpload(fileName)
        id = self.config['identifier'].encode('utf-8')
        accion = 'u'.encode('utf-8')
        if partitions[0] != 'error':
            with open(fileName, 'rb') as f:
                
                for ip, parts in partitions[1].items():
                    modo = 'wb'
                    self.s.connect(ip)
                    for part in parts:
                        
                        modo = modo.encode('utf-8')
                        
                        f.seek(part * uploadSpeed)
                        data = f.read(uploadSpeed)
                        
                        message = []
                        message.append(accion) #accion
                        message.append(id) #identificador de usuario
                        message.append(fileName.encode('utf-8')) #nombre del archivo
                        message.append(modo) #estado
                        message.append(data) #data
                        self.s.send_multipart(message)
                        self.s.recv_multipart()
                        
                        modo = 'ab'
                        
                    self.s.disconnect(ip)
                    
    def download(self, fileName):
        self.loadConfig()
        
        partitions = self.askToDownload(fileName)
        id = self.config['identifier'].encode('utf-8')
        accion = 'd'.encode('utf-8')
        modo = 'wb'
        
        if partitions[0] != 'error':
            for ip, parts in partitions[1].items():
                
                pointerState = '0'.encode('utf-8')
                
                
                self.s.connect(ip)
                
                for part in parts:
                    
                    message = []
                    message.append(accion) #accion
                    message.append(id) #identificador de usuario
                    message.append(fileName.encode('utf-8')) #nombre del archivo
                    message.append(pointerState) #estado del puntero
                    
                    
                    
                    self.s.send_multipart(message)
                    response = self.s.recv_multipart()
                    
                    pointerState = response[0]
                    data = response[1]
            
                    
                    with open(fileName, modo) as f:
                        f.seek(part * uploadSpeed)
                        f.write(data)
                    modo = 'ab'
                
                        
                self.s.disconnect(ip)
                
    def downloadByLink(self, link):
        self.loadConfig()
        
        partitions = self.askToDownloadLink(link)
        accion = 'dl'.encode('utf-8')
        modo = 'wb'
        
        if partitions[0] != 'error':
            for ip, parts in partitions[1].items():
                
                pointerState = '0'.encode('utf-8')
                
                self.s.connect(ip)
                
                for part in parts:
                    
                    message = []
                    message.append(accion) #accion
                    message.append(link.encode('utf-8')) #link del archivo
                    message.append(''.encode('utf-8'))
                    message.append(pointerState) #estado del puntero
                    
                    
                    
                    self.s.send_multipart(message)
                    response = self.s.recv_multipart()
                    
                    pointerState = response[0]
                    data = response[1]
                    fileName = response[2]
            
                    
                    with open(fileName, modo) as f:
                        f.seek(part * uploadSpeed)
                        f.write(data)
                    modo = 'ab'
                
                        
                self.s.disconnect(ip)
        
        
 
Client = CLDrive()
Client.loadConfig()
if argv[1] == 'u':
    Client.upload(argv[2])
    
if argv[1] == 'd':
    Client.download(argv[2])
    
if argv[1] == 'l':
    Client.askForLink(argv[2])
    
if argv[1] == 'dl':
    Client.downloadByLink(argv[2])
# Client.askToUpload(argv[1], int(argv[2]))
# Client.askToDownload(argv[1])