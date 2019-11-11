#!/usr/bin/env python3
import os
import time

print("Running iperf...")
os.system("iperf -s -i 1 -f m > ~/iperf-{}".format(int(time.time())))