from flask import Flask, render_template, jsonify
import time
import json
from pymongo import MongoClient
import zmq
from importlib.machinery import SourceFileLoader
import threading
import socket 

from pathlib import Path
import sys
path = str(Path(__file__).parent.absolute())
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
path = str(Path(Path(Path(__file__).parent.absolute()).parent.absolute()).parent.absolute())
sys.path.insert(0, path)
from lib.config.config import INI
import lib.PPQ as PPQ
import lib.S3_CRUD as crud


app = Flask(__name__)
router = PPQ.Server()

app.run(debug=False,  host='0.0.0.0')