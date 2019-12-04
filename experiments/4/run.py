#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time

def run_client(target, arguments, results_dir):
    buffer_length = arguments.get('buffer_length', 8000)
    time = arguments.get('time', 15)
    udp = arguments.get('udp', False)
    command = "sudo iperf {} 2>&1 | tee {}/{}/{}/local".format(
        " ".join([
            "-u -b 10g" if udp else "",
            "-i 0.5",
            "-t {}".format(time),
            "-f m",
            "-l {}".format(buffer_length),
            "-c {}".format(str(target)),
            "-p 51234"
        ]),
        results_dir, arguments.get("_run"), str(target)
    )
    print(command)
    os.system(command)
    os.system("sudo kill -9 $(pidof iperf)")

    # Then kill server.

def start_server(target, arguments, results_dir):
    udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "timeout 18 sudo iperf {} -s -i 0.5 -f m -p 51235 -D >> {}/{}/{}/local-server".format(
        "-u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )
    os.system(cmd)

if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])
    time.sleep(2)
    run_client(sys.argv[1], args, sys.argv[3])