# https://fastapi.tiangolo.com/deployment/docker/
from flask import Flask
import time
import zmq
import threading

# the first thing that will happend after initialising is a worker/interface will HTTP request a meeting
# after meeting sharing the programs ID and the server will create a chatter thread (bi-directional server->worker unique)

def chatter():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:1000")
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(1)

        #  Send reply back to client
        socket.send(b"World")

threading.Thread(target=chatter).start()


app = Flask(__name__)

# main.py    
@app.route('/')
def index():
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
