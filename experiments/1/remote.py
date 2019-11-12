#!/usr/bin/env python3
import os
import time
import sys

time = int(time.time())
os.system("'{}' > ~/iperf-{}".format(str(sys.argv), time))
print("Running iperf...")
os.system("iperf -s -i 1 -f m > ~/iperf-{}".format(time))