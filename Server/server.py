from sys import argv
import zmq
import os

from secrets import token_urlsafe
from hashlib import sha1
from pprint import pprint

downloadSpeed = 1024**2 #1 megaByte
topRange = 2**160

class SVDrive():
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ipPort = 'tcp://{}:{}'.format(ip, port)
        
        self.hash = sha1(token_urlsafe().encode()).hexdigest()
        self.topHash = int(self.hash, 16)
        
        self.context = zmq.Context()
        
        self.escucha = self.context.socket(zmq.REP)
        self.escucha.bind('tcp://*:{}'.format(port))
        
        self.pregunta = self.context.socket(zmq.REQ)
        
        self.preRange = None
        self.posRange = None
        
        self.nextIp = None
        
    def makeRing(self):
        self.preRange = range(0, self.topHash)
        self.posRange = range(self.topHash, topRange)
        
        self.nextIp = self.ipPort
        
    def waitForActions(self):
        pass
        
    def attachToRIng(self, ringIp):
        self.pregunta.connect(ringIp)
        
        pass
        
        self.pregunta.disconnect(ringIp)
    
    def show(self):
        pprint(vars(self))
        
sv = SVDrive('1111.1111.1111', '1234')
sv.show()
print('-------------------------------')
sv.makeRing()
sv.show()
