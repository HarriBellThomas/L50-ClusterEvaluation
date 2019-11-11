#!/usr/bin/env python3
import os
import time

print("Running iperf...")
os.system("iperf -s > ~/iperf-{}".format(int(time.time())))