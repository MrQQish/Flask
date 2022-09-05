from src import *


class Channel: 
    def __init__(self): 
        pass


    def registerSocket(self, s): 
        with app.app_context():
            try:
                self.channel_thread = threading.Thread(target=self.startSocket, args=(context,s,)).start()
            except Exception as e:
                jsonify({"ERROR": 1, "MESSAGE" : "failed to add socket (%s) to channel threads : %s" % (s, e)}) 

    def startSocket(c,s):
        with app.app_context():
            try:
                socket = c.socket(zmq.REP)
                socket.bind("tcp://*:" + str(s))
                while True:
                    #  Wait for next request from client
                    message = socket.recv()
                    print("Received request: %s" % message)

                    #  Do some 'work'
                    time.sleep(1)

                    #  Send reply back to client
                    socket.send(b"{\"GUID\" : 1, \"RESPONSE\" : \"ALL GOOD\"}")
            except: 
                jsonify({"ERROR": 1, "MESSAGE" : "cannot bind to socket %s" % s}) 