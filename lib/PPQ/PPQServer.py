from random import randint
from collections import OrderedDict
import time
import zmq
import threading

from .PPQChannel import *
from .PPQRouter import *

SERVER_IP = "192.168.15.50"
HEARTBEAT_PORT = 1000

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 3
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat
PPP_ASSIGN = b"\x03"

class ServerChannel(Channel):
    def createSocket(s):
        s.socket = s.context.socket(zmq.REP)
        s.socket.bind("tcp://*:1000")
    
    def work(s):
        #  Wait for next request from client
        message = s.socket.recv()
        print("Received request: %s" % message)
        time.sleep(1)
        #  Send reply back to client
        s.socket.send(b"{\"GUID\" : 1, \"RESPONSE\" : \"ALL GOOD\"}")  


class Server():
    def __init__ (s):
        s.context = zmq.Context()
        s.channel = ServerChannel(s.context)
        s.router = RouterChannel(s.context)


###################################### TEST
if __name__ == "__main__":
    test_server = Server()