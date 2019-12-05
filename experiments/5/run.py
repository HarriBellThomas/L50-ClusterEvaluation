#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import uuid

def start_server(target, arguments, results_dir, i):
    # udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "timeout 20 iperf3 -s -i 0.5 -f m -p 51236 >> {}/{}/{}/local-{} &".format(
        results_dir, arguments.get("_run"), str(target), i
    )
    os.system(cmd)
    # os.system("kill -9 $(pidof iperf3)")


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    for i in range(0, len(sys.argv[1].split(","))):
        run_client(sys.argv[1], args, sys.argv[3], i)
    time.sleep(20)
