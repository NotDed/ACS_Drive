
import zmq
import json
from  hashlib import sha1
import os

from sys import argv

from utilityFunctions import getPartsAndHashes, messageToUpload, decodeMessage, encodeMessage

uploadSpeed = 520#(1024**2)*10 #partes de 10 megabytes
# uploadSpeed = 1024**2 #1 megaByte

class CLDrive():
    
    def __init__(self):
        self.context = zmq.Context()
        self.pregunta = self.context.socket(zmq.REQ)
        
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
    def sendMessageTo(self, ip, encodedMessage):
        self.pregunta.connect(ip)
        self.pregunta.send_multipart(encodedMessage)
        encodedResponse = self.pregunta.recv_multipart()
        self.pregunta.disconnect(ip)
        return encodedResponse
    
    def download(self, ringIp, fileToken):
        actualIp = ringIp
        accepted = False
        
        message = ['download', fileToken]
        message = encodeMessage(message)
        
        #downloading torrent
        while not accepted:
            response = self.sendMessageTo(actualIp, message)
            response = decodeMessage(response)
            
            if response[0] == 'accepted':
                accepted = True
                torrentDict = response[1]
            else:
                actualIp = response[1]
        
        fileName = 'downloads/{}e.{}'.format(torrentDict['fileName'], torrentDict['extension'])
        
        with open(fileName, mode='w'):
            pass
        
        
        completeFileHash = sha1()
        for partTk in torrentDict['parts']:
            
            print('{} \t<- looking for'.format(partTk))
            
            message = ['download', partTk]
            message = encodeMessage(message)
            accepted = False
            while not accepted:
                response = self.sendMessageTo(actualIp, message)
                
                if response[0] == b'"accepted"':
                    print('{} \t<- found'.format(partTk))
                    part = response[1]
                    completeFileHash.update(part)
                    accepted = True
                    with open(fileName, 'ab') as f:
                        f.write(part)
                else:
                    response = decodeMessage(response)
                    actualIp = response[1]
                    
        completeFileHash = completeFileHash.hexdigest()
        if torrentDict['completeFileHash'] == completeFileHash:
            print("Descarga exitosa")
        else:
            print("Algo salió mal en la descarga")
        
    def upload(self, ringIp, fileName):
        actualIp = ringIp
        torrentName, messages = getPartsAndHashes(fileName)
        
        with open(torrentName, 'rb') as f:
            data = f.read()
            torrentSha = sha1(data).hexdigest()
            numericSha = int(torrentSha, 16)
            torrentMessage = messageToUpload(numericSha, data)
            messages.append(torrentMessage)
            
        for message in messages:
            accepted = False
            while not accepted:
                response = self.sendMessageTo(actualIp, message)
                response = decodeMessage(response)
                if response[0] == 'accepted':
                    accepted = True
                else:
                    actualIp = response[1]
                    
        return numericSha
 
Client = CLDrive()
if argv[1] == 'u':
    print(Client.upload(argv[2], argv[3]))
    
if argv[1] == 'd':
    Client.download(argv[2], argv[3])
# Client.askToUpload(argv[1], int(argv[2]))
# Client.askToDownload(argv[1])