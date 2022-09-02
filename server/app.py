# https://fastapi.tiangolo.com/deployment/docker/
from fastapi import FastAPI
import time
import zmq
import threading

def chatter():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(1)

        #  Send reply back to client
        socket.send(b"World")

threading.Thread(target=chatter).start()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

