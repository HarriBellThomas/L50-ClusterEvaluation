#!/usr/bin/env python3
import argparse
import sys
import os
import json

def run(target, arguments, results_dir):
    icmp = arguments.get('icmp', False)  # Use ICMP over UDP.
    tcp = arguments.get('tcp', False)  # Use TCP over UDP.
    size = arguments.get('size', 40)  # Use TCP over UDP.
    bypass_routing_table = arguments.get('bypass_routing_table', False)  # Send directly to interface.
    dont_fragment = arguments.get('dont_fragment', False)  # Set Don't Fragment bit.
    wait = arguments.get('wait', 0)  # Set Don't Fragment bit.
    os.system("sudo traceroute {} {} {} > {}/{}/{}/local".format(
        " ".join([
            "-I" if icmp else ("-T" if tcp else ""),
            "-r" if bypass_routing_table else ""
            "-F" if dont_fragment else "",
            "-q 5",
            "-z {}".format(wait)
        ]), target, size, results_dir, arguments.get("_run"), str(target)
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args, sys.argv[3])