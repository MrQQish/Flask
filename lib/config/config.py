import json
import os
import sys
from pathlib import Path

class _CONFIG:
    def __init__(self):
        base_path = Path(__file__).parent
        conf_path = (base_path / 'config.json').resolve()
        if not os.path.exists(conf_path):
            print("Error: cannot find config.json file in src/keys_server/CombusLookup/config.json")
            sys.exit(1)

        with open(conf_path,'r') as conf_f:
            self.conf = json.load(conf_f)
    
    def get(self,key):
        return self.conf[key]

INI = _CONFIG()


