from src import *
import pymongo

# the first thing that will hserverend after initialising is a worker/interface will HTTP request a meeting
# after meeting sharing the programs ID and the server will create a chatter thread (bi-directional server->worker unique)
########################################################## VEIWS
@app.route('/')
def index():
    return 'OK'

########################################################## API 
@app.route('/registerWorker/<IP>', methods=['GET'])
def registerWorker(IP):
    workers = db.workers
    whisper_port = -1
    
    worker = len(list(workers.find({'IP' : IP})))
    if (not worker): # check if worker has already been registered
        if (not len(list(workers.find()))): # if first worker manually assign the port
            whisper_port = ini["zeromq_port"] + 1
        else: # get the max existing port 
            whisper_port = workers.find().sort("WHISPER", pymongo.DESCENDING).limit(1)[0]["WHISPER"] + 1 # return the next PORT inline
        if (whisper_port < 0):
            return jsonify({"ERROR": 1, "MESSAGE" : "failed to search IP in DB"})
        # launch the the new websocket thread 
        try:
            channel_stack[whisper_port] = channels.WorkerChannel(whisper_port)
        except Exception as e:
            return jsonify({"ERROR": 1, "MESSAGE" : "failed to register socket on port %s" % whisper_port})
        
        # this needs to be moved until after the cokects have been tested 
        # try:
        #     workers.insert_one({'IP' : IP, 'WHISPER' : whisper_port})
        # except Exception as e: 
        #     return jsonify({"ERROR": 1, "MESSAGE" : "failed to register socket on db :: %s" % e})

        # else ALL GOOOD
        return jsonify({"ERROR": 0, "YELL": ini["zeromq_port"], "WHISPER" : whisper_port})
    else:
        return jsonify({"ERROR": 1, "MESSAGE" : "IP is already included", "YELL": ini["zeromq_port"], "WHISPER" : whisper_port})

