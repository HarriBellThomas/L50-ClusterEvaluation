#!/usr/bin/env python3
import time
import sys
import os
sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import base64
import socket
from experiment import prepare_for_experiment

time = int(time.time())
argsEncodedBytes = base64.b64decode(sys.argv[1].encode("utf-8"))
argsEncodedJson = str(argsEncodedBytes, "utf-8")
args = json.loads(argsEncodedJson)

ip = str(socket.gethostbyname(socket.gethostname()))
results_dir = prepare_for_experiment(args, ip, "(?)")

print("Running iperf...")
os.system("iperf -s -i 1 -f m >> {}/remote".format(results_dir))