from src import *
import time



class Channel: 
    def __init__(self, port): 
        self.context = context
        
        self.port = port
        self.run = True

        self.channel = 0 # threading.Thread()
        self.socket = 0

        with app.app_context():
            self.createChannel()


    def registerServer():
        pass

    def registerWorker():
        pass

    def ping():
        pass

    def createChannel(self): 
        try:
            self.startSocket()
        except Exception as e: 
            jsonify({"ERROR": 1, "MESSAGE" : "cannot bind to socket %s" % self.s, "EXCEPTION" : e }) 

        try:
            self.channel_thread = threading.Thread(target=self.startChannel, args=()).start()
            # self.log("connection started")
        except Exception as e:
            jsonify({"ERROR": 1, "MESSAGE" : "failed to add socket (%s) to channel threads : %s" % (self.s, e)}) 

    def startChannel(self):
        while self.run:
            try:
                self.handleMessages()
            except Exception as e:
                jsonify({"ERROR": 1, "MESSAGE" : "cannot handle message", "EXCEPTION" : e }) 
            

    def stopChannel(self):
        self.run = False
        self.channel_thread.join()

    def log(self, message):
        # time = time.strftime("%Y%M%D-%H:%M:%S", time.time())
        _time = str(time.strftime("%H:%M:%S", time.localtime()))
        print("%s [ %s ]: %s" % (_time, self.port, str(message)))
        
    def getChannelInformation(self):
        return {}

    def startSocket():
        raise NotImplementedError()

    def handleMessages():
        raise NotImplementedError()


class WorkerChannel(Channel):
    def startSocket(self):
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:" + str(self.s))

    def handleMessages(self):
        #  Wait for next request from client
        message = self.socket.recv()
        print("Received request: %s" % message)


        #  Send reply back to client
        self.socket.send(b"{\"GUID\" : 1, \"RESPONSE\" : \"ALL GOOD\"}")
                

class TestChannel(Channel):
    def startSocket(self):
        with app.app_context():
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind("tcp://*:" + str(self.port))

    def handleMessages(self):
        #  Wait for next request from client
        message = self.socket.recv()
        # print("Received request: %s" % message)
        self.log(message.decode('ascii'))

        #  Send reply back to client
        self.socket.send(b"world")