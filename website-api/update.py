#!/usr/bin/env python2
from __future__ import print_function
import json
import yaml
import subprocess
import re
import requests
from collections import Counter
import sys
import time


with open("config.yaml", "r") as file_handle:
        config = yaml.load(file_handle)

alfred_call = "alfred-json -r 159 -z -f json"
vnstat_call = "vnstat -d -i eth0"

document = {}

# ALFRED
if config['alfred']:
        # query alfred for node and client count
        child = subprocess.check_output(alfred_call.split(" "))
        data = json.loads(child)

        nodes = 0
        clients = 0
        for mac, router in data.iteritems():
                if 'clients' not in router:
                        continue
                nodes += 1
                clients += int(router['clients']['wifi'])

        document['nodes'] = nodes
        document['clients'] = clients


# VNSTAT
def to_kiB(input):
    amount, unit = input.split(" ")
    if unit == 'GiB':
        return float(amount) * 1024 * 1024
    elif unit == 'MiB':
        return float(amount) * 1024
    elif unit == 'KiB':
        return float(amount)

if config['vnstat']:
        # get daily (tx, rx, total) average for the last 7 days
        child = subprocess.check_output(vnstat_call.split(" "))
        lines = child.split("\n")

        pattern = '\s+(?P<date>[0-9\/]{8})\s+(?P<rx>[0-9]+\.[0-9]+\s[kKMGTiB]{2,3})[\s|]+(?P<tx>[0-9]+\.[0-9]+\s[kKMGTiB]{2,3})[\s|]+(?P<total>[0-9]+\.[0-9]+\s[kKMGTiB]{2,3})[\s|]+(?P<avg>[0-9]+\.[0-9]+\s[kMGT]*bit\/s)'
        expr = re.compile(pattern)

        # traffic counter
        local_traffic = Counter({'rx': 0, 'tx': 0})
        for i in xrange(-5 - 7, -4):
                line = lines[i]
                result = expr.match(line)

                # parse amount and unit, convert to kiB, strip unit
                local_traffic['rx'] += to_kiB(result.group('rx'))
                local_traffic['tx'] += to_kiB(result.group('tx'))

        # take 7 days average
        # and readd unit
        for k, v in local_traffic.iteritems():
                local_traffic[k] = v/7

        print("local traffic is {0}".format(dict(local_traffic)))

        document['traffic'] = local_traffic

# COLLECT
if config['collect']:
        external_traffic = Counter({'rx': 0, 'tx': 0})
        for url in config['collect']:
                # sum up traffic
                try:
                        result = requests.get(url)
                        doc = json.loads(result.text)
                except Exception as ex:
                        print("[{host}] {ex}".format(host=url, ex=ex))
                        continue

                traffic = Counter(doc['traffic'])

                # add to sum
                external_traffic = external_traffic + traffic

                print("aggregated {} with {}".format(url, dict(traffic)))

        if 'traffic' in document:
                document['traffic'] += external_traffic
        else:
                document['traffic'] = exernal_traffic

        print("total traffic is {}".format(dict(document['traffic'])))


document['changed'] = int(time.time())

if config['target']:
        with open(config['target'], "w") as handle:
                handle.write(json.dumps(document))
else:
        print(json.dumps(document))
