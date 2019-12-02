#!/usr/bin/env python3
import argparse
import sys
import os
sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
from experiment import prepare_for_experiment

def run(target, arguments, results_dir):
    size = arguments.get('size', 56)  # Payload size in bytes.
    interval = arguments.get('interval', 0.1)  # Inter-packet wait time, seconds.
    flood = arguments.get('flood', False)  # Send at maximum speed.
    iterations = arguments.get("iterations", 1000)  # Send x pings.
    duration = arguments.get("duration", False)  # Send for x seconds.

    speed = "-f" if flood else "-i {}".format(interval)
    os.system("sudo ping {} {} > {}/{}/{}/local".format(
        " ".join([
            "-s {}".format(size),
            "-n {}".format(iterations) if not duration else "",
            "-w {}".format(duration) if duration else "",
            "-l {}".format(size),
            "-f" if flood else ""
        ]),
        str(target), results_dir, arguments.get("_run"), str(target)
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args, sys.argv[3])