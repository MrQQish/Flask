
from random import randint
from collections import OrderedDict
import time
import zmq
import threading

SERVER_IP = "192.168.15.50"
HEARTBEAT_PORT = 1000

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 3
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat


class Channel():
    # open a socket, create the channel thread, and start
    def __init__(s, context):
        s.context = context
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

class WorkerHeartbeat(Channel):
    def createSocket(s):
        s.poller = zmq.Poller()
        s.socket = s.context.socket(zmq.DEALER) # DEALER
        
        s.identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        s.socket.setsockopt(zmq.IDENTITY, s.identity)
        
        s.liveness = HEARTBEAT_LIVENESS
        s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        s.interval = HEARTBEAT_INTERVAL

        s.poller.register(s.socket, zmq.POLLIN)
        s.socket.connect("tcp://%s:%s" % (SERVER_IP, HEARTBEAT_PORT))
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
                # print("I: Queue heartbeat")
                s.liveness = HEARTBEAT_LIVENESS
            else:
                print("E: Invalid message: %s" % frames)
            s.interval = INTERVAL_INIT
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
                s.socket = s.createSocket()
                s.liveness = HEARTBEAT_LIVENESS

        if time.time() > s.heartbeat_at:
            s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
            # print("I: socket heartbeat")
            s.socket.send(PPP_HEARTBEAT)

class WorkerChannel(Channel):
    def createSocket(s):
        s.socket = s.context.socket(zmq.REP)
        s.socket.bind("tcp://*:1000")
    
    def work(s):
        #  Wait for next request from client
        message = s.socket.recv()
        print("Received request: %s" % message)

        #  Send reply back to client
        s.socket.send(b"{\"GUID\" : 1, \"RESPONSE\" : \"ALL GOOD\"}")  

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

##########################################################################

class WorkerID(object):
    def __init__(self, address):
        self.address = address
        self.expiry = time.time() + HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS

class WorkerQueue(object):
    def __init__(self):
        self.queue = OrderedDict()

    def ready(self, worker):
        self.queue.pop(worker.address, None)
        self.queue[worker.address] = worker

    def purge(self):
        """Look for & kill expired workers."""
        t = time.time()
        expired = []
        for address, worker in self.queue.items():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            print("W: Idle worker expired: %s" % address)
            self.queue.pop(address, None)

    def next(self):
        address, worker = self.queue.popitem(False)
        return address

class Router():
    def __init__ (s):
        s.context = zmq.Context()
        # s.FlaskContext = FlaskContext

        s.frontend = s.context.socket(zmq.ROUTER) # ROUTER
        s.backend = s.context.socket(zmq.ROUTER)  # ROUTER
        s.frontend.bind("tcp://*:5555") # For clients
        s.backend.bind("tcp://*:5556")  # For workers

        s.poll_workers = zmq.Poller()
        s.poll_workers.register(s.backend, zmq.POLLIN)

        s.poll_both = zmq.Poller()
        s.poll_both.register(s.frontend, zmq.POLLIN)
        s.poll_both.register(s.backend, zmq.POLLIN)

        s.workers = WorkerQueue()

        s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL

        s.startRouter()


    def startRouter(s):
        while True:
            if len(s.workers.queue) > 0:
                poller = s.poll_both
            else:
                poller = s.poll_workers
            socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

            # Handle worker activity on backend
            if socks.get(s.backend) == zmq.POLLIN:
                # Use worker address for LRU routing
                frames = s.backend.recv_multipart()
                if not frames:
                    break

                address = frames[0]
                s.workers.ready(WorkerID(address))

                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) == 1:
                    if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
                        print("E: Invalid message from worker: %s" % msg)
                else:
                    s.frontend.send_multipart(msg)

                # Send heartbeats to idle workers if it's time
                if time.time() >= s.heartbeat_at:
                    for worker in s.workers.queue:
                        msg = [worker, PPP_HEARTBEAT]
                        s.backend.send_multipart(msg)
                    s.heartbeat_at = time.time() + HEARTBEAT_INTERVAL
            if socks.get(s.frontend) == zmq.POLLIN:
                frames = s.frontend.recv_multipart()
                if not frames:
                    break

                frames.insert(0, s.workers.next())
                s.backend.send_multipart(frames)


            s.workers.purge()

