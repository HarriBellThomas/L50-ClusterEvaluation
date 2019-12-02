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
    bidirectional = arguments.get("bidir", False)
    os.system("sudo iperf3 {} 2>&1 | tee {}/{}/{}/local".format(
        " ".join([
            "-u -b 1000m" if udp else ""
            "-i 0.5",
            "-t {}".format(time),
            "-f m",
            "-l {}".format(buffer_length),
            "-c {}".format(str(target)),
            "--bidir" if bidirectional else ""
        ]),
        results_dir, arguments.get("_run"), str(target)
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args, sys.argv[3])