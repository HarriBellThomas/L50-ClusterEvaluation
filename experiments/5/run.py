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
    cmd = "sudo iperf {} -s -i 0.5 -f m -p 51236 -l 1M -D -t 23 > {}/{}/{}/local ;".format(
        "-U -u" if udp else "", 
        results_dir, arguments.get("_run"), str(target)
    )
    cmd = cmd + "sleep 23; sudo kill -9 $(pidof iperf); exit;"

    _id = str(uuid.uuid4())
    tmux_cmd = "tmux new-session -d -s evaluation-{};".format(_id)
    tmux_cmd = tmux_cmd + "tmux send -t evaluation-{} \"{}\" ENTER; ".format(_id, cmd)
    os.system(cmd)


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    start_server(sys.argv[1], args, sys.argv[3])