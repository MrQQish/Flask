from src import *
import pymongo

# the first thing that will hserverend after initialising is a worker/interface will HTTP request a meeting
# after meeting sharing the programs ID and the server will create a chatter thread (bi-directional server->worker unique)
########################################################## VEIWS
@app.route('/')
def index():
    return 'OK'


################################################# WEB APP
@app.route('/')
def home():
    loadState()
    return render_template("dash.html")

################################################# WEB API 


# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
@app.route('/uploader', methods = ['GET', 'POST'])
@stateChange
def upload_file():
    f = request.files['file'] # File in react
    f.save(os.path.join('data/inputs', f.filename))
    return '{"error" : "0"}'



@app.route('/read_rainfile', methods = ['GET', 'POST'])
def read_rainfile():
    if request.method == 'POST':
        file = request.form.getlist('event_file')
    else:
        file = request.args.get('event_file')
    
    events = {}
    for event in file:
        data = open(os.path.join('data/inputs', event), 'r')
        events.update(read_rain.read_pjw(data))
        
    turbo.push(turbo.update(render_template('events.html', events=events), 'event_list'))

    return jsonify(events)




@app.route('/get_inputs', methods = ['GET', 'POST'])
def get_inputs():
    files = os.listdir('data/inputs/')
    return jsonify(files)




###################################################################### WORKER API

# @app.route('/get_workers', methods = ['GET', 'POST'])
# def get_workers():
#     workers = dict(request.form)
#     # print(inspect.getmembers(worker_list))

#     worker_list = []
#     for worker in workers:
#         ID = worker.split('[')[0]
#         if ID not in worker_list:
#             worker_list.append(ID)

#     turbo.push(turbo.replace(render_template('celery.html', worker_list=worker_list), 'task_list'))
#     return '{"error" : "0"}'
    
# @app.route('/send_tasks', methods = ['GET', 'POST'])
# def send_tasks():
    
#     if request.method == 'POST':
#         inputs = request.form.getlist('event_input')
#     else:
#         inputs = request.args.get('event')
    
#     app = Celery()
#     for input in inputs:
#         res = app.send_task('test',)
#         print(res)
    
    
#     return jsonify(inputs)



###############################################################  CRUD 

@app.route('/upload', methods=['POST'])
@stateChange
def upload():    
    f = request.files['file'] # File in react
    path = os.path.join('./data/inputs', f.filename)
    f.save(path)

    file = open(path)
    return crud.upload(file)


@app.route('/download/<bucket>/<key>', methods=['GET'])
def download(bucket, key):
    return crud.download(bucket,key)



@app.route('/delete/<bucket>/<key>', methods=['GET'])
@stateChange
def delete(bucket, key): 
    return crud.delete(bucket,key)


@app.route('/list/<bucket>', methods=['GET'])
def list(bucket): 
    results = crud.list(bucket)
    return '{"list":"0"}'


# ########################################################## API 
# @app.route('/registerWorker/<IP>', methods=['GET'])
# def registerWorker(IP):
#     workers = db.workers
#     whisper_port = -1
    
#     worker = len(list(workers.find({'IP' : IP})))
#     if (not worker): # check if worker has already been registered
#         if (not len(list(workers.find()))): # if first worker manually assign the port
#             whisper_port = ini["zeromq_port"] + 1
#         else: # get the max existing port 
#             whisper_port = workers.find().sort("WHISPER", pymongo.DESCENDING).limit(1)[0]["WHISPER"] + 1 # return the next PORT inline
#         if (whisper_port < 0):
#             return jsonify({"ERROR": 1, "MESSAGE" : "failed to search IP in DB"})
#         # launch the the new websocket thread 
#         try:
#             channel_stack[whisper_port] = channels.WorkerChannel(whisper_port)
#         except Exception as e:
#             return jsonify({"ERROR": 1, "MESSAGE" : "failed to register socket on port %s" % whisper_port})
        
#         # this needs to be moved until after the cokects have been tested 
#         # try:
#         #     workers.insert_one({'IP' : IP, 'WHISPER' : whisper_port})
#         # except Exception as e: 
#         #     return jsonify({"ERROR": 1, "MESSAGE" : "failed to register socket on db :: %s" % e})

#         # else ALL GOOOD
#         return jsonify({"ERROR": 0, "YELL": ini["zeromq_port"], "WHISPER" : whisper_port})
#     else:
#         return jsonify({"ERROR": 1, "MESSAGE" : "IP is already included", "YELL": ini["zeromq_port"], "WHISPER" : whisper_port})

