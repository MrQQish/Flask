import zmq
import uuid
import socket   
import requests
import hashlib
import json


from pathlib import Path
import sys
path = str(Path(__file__).parent.absolute())
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
path = str(Path(Path(Path(__file__).parent.absolute()).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
from lib.config.config import INI
from lib.PPQ.PPQChannel import *
from lib.PPQ.PPQRouter import *
from lib.PPQ.PPQWorker import *
from lib.PPQ.PPQServer import *


context = zmq.Context()
hostname = socket.gethostname()   
IP = socket.gethostbyname(hostname)  
MAC = hex(uuid.getnode())
SERVER = IP
SERVER_API = IP + ":5000"
UUID = str(uuid.uuid4().fields[-1])[:5]
GUID = hashlib.md5(MAC.encode('ascii') + UUID.encode('ascii')).hexdigest()


def registerServer():
    # check if we have already been registered on the server
    server_url = "http://%s/" % (SERVER)
    request_registration_url = server_url + "%s/%s" % ("registerWorker", IP)
    print ("REGISTERING: ", request_registration_url)
    r = requests.get("http://%s/%s/%s" % (SERVER_API,"registerWorker",IP))
    print (r, r.json())

    response = r.json()
    if (not response["ERROR"]):
        # #  Socket to talk to server
        whisper = context.socket(zmq.REQ)
        whisper.connect("tcp://%s:%s" % (SERVER, response["WHISPER"]))
        whisper.send(("[ %s ] WHISPER CHANNEL TEST" % GUID).encode('ascii'))
        message = json.loads(whisper.recv())
        print("[ %s ] RESPONSE %s " % (message["GUID"], message["RESPONSE"]))

        # check the yell channel 
        yell = context.socket(zmq.REQ)
        yell.connect("tcp://%s:%s" % (SERVER, response["YELL"]))
        yell.send(("[ %s ] YELL CHANNEL TEST" % GUID).encode('ascii'))
        message = json.loads(yell.recv())
        print("[ %s ] RESPONSE %s " % (message["GUID"], message["RESPONSE"]))


if __name__ == "__main__":    
    # first establish out ID and IP 
    print("WORKER ", GUID, " : ", IP)

    registerServer()
