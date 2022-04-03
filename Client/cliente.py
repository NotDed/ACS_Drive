
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
        
    def addServer(self, ip, storage):
        self.s.connect('tcp://localhost:8001')
        
        message = {}
        message['accion'] = 'asv'
        message['ip'] = ip
        message['storage'] = storage

        self.s.send_json(message)
        
        response = self.s.recv_json()
        
        print(response)
        
    def askToUpload(self, fileName, partCount):
        self.s.connect('tcp://localhost:8001')
        
        id = self.config['identifier']
        
        message = {}
        message['accion'] = 'u'
        message['id'] = id
        message['fileName'] = fileName
        message['partCount'] = partCount

        self.s.send_json(message)
        
        response = self.s.recv_json()
        
        print(response)
        
    def askToDownload(self, fileName):
        self.s.connect('tcp://localhost:8001')
        
        id = self.config['identifier']
        
        message = {}
        message['accion'] = 'd'
        message['id'] = id
        message['fileName'] = fileName

        self.s.send_json(message)
        
        response = self.s.recv_json()
        
        print(response)
        
        
 
Client = CLDrive()
Client.loadConfig()
# Client.askToUpload(argv[1], int(argv[2]))
# Client.askToDownload(argv[1])