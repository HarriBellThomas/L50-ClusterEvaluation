#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json

def run(target, arguments, results_dir):
    buffer_length = arguments.get('buffer_length', 80000)
    time = arguments.get('time', 5)
    udp = arguments.get('udp', False)
    os.system("iperf {} 2>&1 | tee {}/{}/{}/local".format(
        time, str(target), buffer_length, 
        " ".join([
            "-u" if udp else ""
            "-i 1",
            "-t {}".format(time),
            "-f m",
            "-l {}".format(buffer_length),
            "-c {}".format(str(target))
        ]),
        results_dir, arguments.get("_run"), str(target)
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args, sys.argv[3])