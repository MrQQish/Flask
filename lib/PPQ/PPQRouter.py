
from random import randint
from collections import OrderedDict
import time
import zmq
import threading


from .PPQChannel import *

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

class WorkerID(object):
    def __init__(self, address):
        self.address = address # unique identifier
        self.IP = 0
        self.PORT = 0
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

class RouterChannel(Channel):
    def createSocket(s):
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
        


    def work(s):
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
                s.alive = False


            # re ready the worker in the queue
            address = frames[0]
            s.workers.ready(WorkerID(address))
            print(address, frames)

            # Validate control message, or return reply to client
            msg = frames[1:]
            if len(msg) == 1:
                if msg[0] not in (PPP_READY, PPP_HEARTBEAT, PPP_ASSIGN):
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
                s.alive = False

            frames.insert(0, s.workers.next())
            s.backend.send_multipart(frames)


        s.workers.purge()


###################################### TEST
if __name__ == "__main__":
    test_worker = Router()