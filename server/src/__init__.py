from flask import Flask, render_template, jsonify
import time
import json
from pymongo import MongoClient
import zmq
from importlib.machinery import SourceFileLoader
import threading
import socket 


app = Flask(__name__)
db = MongoClient().floodx
context = zmq.Context()

global ini 
ini = json.loads(open("server/config.json", 'r').read())
hostname = socket.gethostname()   
IP = socket.gethostbyname(hostname)  
ini["IP"] = IP

global channel_stack 
channel_stack = {}

###################################################################
from src import channels
from src import routes

channel_stack[ini["zeromq_port"]] = channels.TestChannel(ini["zeromq_port"])

app.run(debug=False,  host='0.0.0.0')