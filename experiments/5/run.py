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
    cmd = "sudo iperf {} -s -f m -p 51236 -l 65000 -D -t 23 > {}/{}/{}/local".format(
        "-U -u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )

    _id = str(uuid.uuid4())
    tmux_cmd = "tmux new-session -d -s recipient-container;".format()
    tmux_cmd = tmux_cmd + "tmux send -t recipient-container \"{}\" ENTER; ".format(cmd)
    os.system(tmux_cmd)


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])