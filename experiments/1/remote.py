#!/usr/bin/env python3
import os
import time
import sys
import json
import base64

time = int(time.time())
argsEncodedBytes = base64.b64decode(sys.argv[1].encode("utf-8"))
argsEncodedJson = str(argsEncodedBytes, "utf-8")
args = json.loads(argsEncodedJson)
os.system("echo 'Arguments: {}' > ~/iperf-{}".format(args, time))

print("Running iperf...")
os.system("iperf -s -i 1 -f m > ~/iperf-{}".format(time))