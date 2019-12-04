#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time

def run_client(target, arguments, results_dir):
    buffer_length = arguments.get('buffer_length', 80000)
    time = arguments.get('time', 5)
    udp = arguments.get('udp', False)
    command = "sudo iperf {} 2>&1 | tee {}/{}/{}/local".format(
        " ".join([
            "-u" if udp else "",
            "-i 0.5",
            "-t {}".format(time),
            "-f m",
            "-l {}".format(buffer_length),
            "-c {}".format(str(target)),
            "-b 10g"
        ]),
        results_dir, arguments.get("_run"), str(target)
    )
    print(command)
    os.system(command)

    # Then kill server.

def start_server(target, arguments, results_dir):
    udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "sudo iperf {} -s -i 0.5 -f m & >> {}/{}/{}/local-server".format(
        "-u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )

if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])
    time.sleep(2)
    run_client(sys.argv[1], args, sys.argv[3])