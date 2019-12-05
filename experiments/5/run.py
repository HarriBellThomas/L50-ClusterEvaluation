#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import uuid

def start_server(target, arguments, results_dir):
    udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "timeout 20 iperf {} -s -i 0.5 -f m -p 51236 -l 65000 2>&1 | tee {}/{}/{}/local".format(
        "-U -u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )
    os.system(cmd)


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])