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
    duration = arguments.get('duration', 5)  # Run for x seconds.

    speed = "-f" if flood else "-i {}".format(interval)
    os.system("sudo ping {} -q -s {} -w {} {} 2>&1 | tee {}/{}/{}/local".format(
        speed, size, duration, str(target), results_dir, arguments.get("_run"), str(target)
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args, sys.argv[3])