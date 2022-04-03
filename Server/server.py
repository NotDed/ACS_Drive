import zmq
import os

from utilityFunctions import decodeMessage, decodeParams, getPaths, makeOrVerify

downloadSpeed = 1024**2

mainDir = 'Data'

class SVDrive():
    pass