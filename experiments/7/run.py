#!/usr/bin/env python3
import argparse
import sys
import os
# sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import uuid

def start_server(target, arguments, results_dir):
    # udp = arguments.get("udp", False)

    print("Running tcpdump server...")
    cmd = "timeout 20 sudo tcpdump -i eth0 -nn -s0 -w {}/{}/{}/local.pcap udp &".format(
        results_dir, arguments.get("_run"), str(target)
    )
    os.system(cmd)
    # os.system("kill -9 $(pidof iperf3)")


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])
    time.sleep(20)
