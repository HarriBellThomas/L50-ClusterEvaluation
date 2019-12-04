#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time

def start_server(target, arguments, results_dir):
    udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "timeout 18 sudo iperf {} -s -i 0.5 -f m -p 51235 -D >> {}/{}/{}/local-server".format(
        "-u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )
    os.system(cmd)
    os.system("sudo kill -9 $(pidof iperf)")


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])