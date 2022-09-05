from flask import Flask, render_template, jsonify
import time
import json
from pymongo import MongoClient
import zmq
from importlib.machinery import SourceFileLoader
import threading



app = Flask(__name__)
db = MongoClient().floodx
context = zmq.Context()

global ini 
ini = json.loads(open("server/config.json", 'r').read())

global channel_threads 
channel_threads = {}

###################################################################
from src import channels
from src import routes

channels.registerSocket(ini["zeromq_port"])

app.run(debug=False,  host='0.0.0.0')