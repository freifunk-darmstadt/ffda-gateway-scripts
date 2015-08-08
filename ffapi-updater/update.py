#!/usr/bin/env python3
import yaml
import json
import requests
import requests.exceptions
import sys
from datetime import datetime

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

with open(config['template'], 'r') as base_file:
    base = json.load(base_file)

# update timestamp
base['state']['lastchange'] = datetime.now().isoformat()

# parse node count from meshviewer v1 api
nodes, clients = 0, 0
try:
    nodelist = requests.get(config['nodelist']).json()

    for node in nodelist.get('nodes', []):
        clients += node['status']['clients']
        if node['status']['online']:
            nodes += 1
except requests.exceptions.RequestException as ex:
    print(ex, file=sys.stderr)

# update node count
base['state']['nodes'] = nodes

# dump json
out = json.dumps(base, sort_keys=True, indent=4)

if 'target' in config:
    with open(config['target'], 'w') as handle:
        handle.write(out)
else:
    print(out)
