#!/usr/bin/env python3
import os
import time
import sys
import json
import base64

time = int(time.time())
argsSafeEncodedBytes = base64.urlsafe_b64encode(sys.argv[1].encode("utf-8"))
argsSafeEncodedJson = str(argsSafeEncodedBytes, "utf-8")
args = json.loads(argsSafeEncodedJson)
os.system("echo 'Arguments: {}' > ~/iperf-{}".format(args, time))

print("Running iperf...")
os.system("iperf -s -i 1 -f m > ~/iperf-{}".format(time))