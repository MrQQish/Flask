from random import randint
from collections import OrderedDict
import time
import zmq
import threading

class Channel():
    # open a socket, create the channel thread, and start
    def __init__(s, context):
        s.context = context
        s.identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        s.createSocket()        
        s.startChannel()
        s.channelThread = threading.Thread(target=s.channelMain, args=()).start()

    def createSocket(s, *args, **kwargs):
        raise NotImplementedError()
        
    def startChannel(s):
        s.alive = True 
        s.run = True 

    def channelMain(s):
        while s.alive:
            if s.run:
                s.work()

    def work(s):
        raise NotImplementedError()

    def stopChannel(s):
        s.alive = False 
        s.run = False 
        s.channelThread.join() 