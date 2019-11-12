#!/usr/bin/env python3
import os
import time
import sys
import json

time = int(time.time())
args = json.loads(sys.argv[1])
os.system("echo 'Arguments: {}' > ~/iperf-{}".format(args, time))

print("Running iperf...")
os.system("iperf -s -i 1 -f m > ~/iperf-{}".format(time))