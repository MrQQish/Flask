
from random import randint
from collections import OrderedDict
import time
import zmq
import threading

from .PPQChannel import *

SERVER_IP = "192.168.15.50"
HEARTBEAT_PORT = 5556

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 3
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat


class WorkerHeartbeat(Channel):
    def createSocket(s):
        s.poller = zmq.Poller()
        s.socket = s.context.socket(zmq.DEALER) # DEALER
        
        s.socket.setsockopt(zmq.IDENTITY, s.identity)
        
        s.liveness = HEARTBEAT_LIVENESS
        s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        s.interval = HEARTBEAT_INTERVAL

        s.poller.register(s.socket, zmq.POLLIN)
        s.socket.connect("tcp://%s:%s" % ("localhost", HEARTBEAT_PORT))
        s.socket.send(PPP_READY)

    
    def work(s):
        socks = dict(s.poller.poll(HEARTBEAT_INTERVAL * 1000))

        # Handle socker activity on backend
        if socks.get(s.socket) == zmq.POLLIN:
            #  Get message
            #  - 3-part envelope + content -> request
            #  - 1-part HEARTBEAT -> heartbeat
            frames = s.socket.recv_multipart()
            if not frames:
                s.stopChannel() # Interrupted

            if len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
                print("I: Queue heartbeat")
                s.liveness = HEARTBEAT_LIVENESS
            else:
                print("E: Invalid message: %s" % frames)
            s.interval = INTERVAL_INIT
            time.sleep(1)  # Do some heavy work this is required to keep the timing 
        else:
            s.liveness -= 1
            if s.liveness == 0:
                print("W: Heartbeat failure, can't reach queue")
                print("W: Reconnecting in %0.2fs..." % s.interval)
                time.sleep(s.interval)

                if s.interval < INTERVAL_MAX:
                    s.interval *= 2
                s.poller.unregister(s.socket)
                s.socket.setsockopt(zmq.LINGER, 0)
                s.socket.close()
                # s.socket = s.createSocket()
                s.createSocket()
                s.liveness = HEARTBEAT_LIVENESS

        if time.time() > s.heartbeat_at:
            s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
            # print("I: socket heartbeat")
            s.socket.send(PPP_HEARTBEAT)

class WorkerChannel(Channel):
    def createSocket(s):
        s.socket = s.context.socket(zmq.REQ)
        s.socket.connect("tcp://%s:1000" % SERVER_IP)
    
    def work(s):
        print("Sending request  …" )
        s.socket.send(b"Hello")

        #  Get the reply.
        message = s.socket.recv()
        print("Received reply [ %s ]" % ( message))

class Worker():
    def __init__(s):    
        s.context = zmq.Context()

        s.liveness = HEARTBEAT_LIVENESS
        s.interval = INTERVAL_INIT

        s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        s.cycles = 0
        s.run = True
        s.worker = WorkerChannel(s.context)
        s.heartbeat = WorkerHeartbeat(s.context)


if __name__ == "__main__":
    test_worker = Worker()