from src import *
import pymongo



################################################### COMPONENTS
# make a way to update individual componetents as well as all components

@app.route('/getComponents', methods=['POST','GET'])
def getComponents():
    turbo.push(turbo.replace(render_template('components/input.html'), 'inputs-component'))
    # turbo.push(turbo.replace(render_template('input.html'), 'inputs'))
    # turbo.push(turbo.replace(render_template('input.html'), 'inputs'))
    return '{"error" : "0"}'

@app.route('/updateComponents', methods=['POST','GET'])
def updateComponents():
    with app.app_context():
        #get all the shit 
        inputs = json.loads(getInputs().data.decode("ascii"))

        # update all the shit
        turbo.push(turbo.replace(render_template('veiws/input.html', inputs=inputs), 'inputs-veiw'))
        return '{"error" : "0"}'

def stateChange(func): # This is the wrapper that is called after each request to API/Frontend components
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print("state updated")
        updateComponents()
        return result
    return wrapper




# the first thing that will hserverend after initialising is a worker/interface will HTTP request a meeting
# after meeting sharing the programs ID and the server will create a chatter thread (bi-directional server->worker unique)
########################################################## VEIWS
@app.route('/')
def home():
    return render_template("dash.html")




################################################# FILE API 
# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
# should be connected to the an S3 buck on AWS or localstack
# need the ability to upload from local file or from bytestream 
# need to be able to copy
@app.route('/upload/<bucket>/<key>', methods = ['POST'])
@stateChange
def uploadInput():
    f = request.files['file'] # File in react
    if (not os.path.isdir(path)):
        os.makedirs(os.path.join('data/inputs'))
    f.save(os.path.join('data/inputs', f.filename))
    file =  open(os.path.join('data/inputs', f.filename), "rb") 

    return crud.upload(file)
    # return '{"error" : "0"}'


@app.route('/getInputs', methods = ['GET', 'POST'])
def getInputs():
    files = os.listdir('data/inputs/')
    return jsonify(files)




# @app.route('/read_rainfile', methods = ['GET', 'POST'])
# @stateChange
# def read_rainfile():
#     if request.method == 'POST':
#         file = request.form.getlist('event_file')
#     else:
#         file = request.args.get('event_file')
    
#     events = {}
#     for event in file:
#         data = open(os.path.join('data/inputs', event), 'r')
#         events.update(read_rain.read_pjw(data))
        
#     turbo.push(turbo.update(render_template('events.html', events=events), 'event_list'))

#     return jsonify(events)


###################################################################### WORKER API
@app.route('/get_workers', methods = ['GET', 'POST'])
def get_workers():
    # workers = dict(request.form)
    # print(inspect.getmembers(worker_list))
    # access the worker queue object
    with app.app_context:
        worker_list = []
        for worker in workers:
            ID = worker.split('[')[0]
            if ID not in worker_list:
                worker_list.append(ID)

        turbo.push(turbo.replace(render_template('celery.html', worker_list=worker_list), 'task_list'))
        return '{"error" : "0"}'


@app.route('/download/<bucket>/<key>', methods=['GET'])
def download(bucket, key):
    return crud.download(bucket,key)

#@app.route('/download/<bucket>/<key>', methods=['GET'])
#def download(bucket, key):
 #   return crud.download(bucket,key)



@app.route('/delete/<bucket>/<key>', methods=['GET'])
@stateChange
def delete(bucket, key): 
    return crud.delete(bucket,key)


@app.route('/list/<bucket>', methods=['GET'])
def list(bucket): 
    results = crud.list(bucket)
    return '{"list":"0"}'

