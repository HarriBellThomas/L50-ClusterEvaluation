#!/usr/bin/env python3
import argparse
import sys
import os
import json
from experiments.experiment import prepare_for_experiment

def run(target, arguments):
    results_dir = prepare_for_experiment(arguments)
    size = arguments.get('size', 56)  # Payload size in bytes.
    interval = arguments.get('interval', 0.1)  # Inter-packet wait time, seconds.
    flood = arguments.get('flood', false)  # Send at maximum speed.
    duration = arguments.get('duration', 5)  # Run for x seconds.

    speed = "-f" if flood else "-i {}".format(interval)
    os.system("sudo ping {} -s {} -w {} {} > {}/local".format(
        speed, size, duration, str(target), results_dir
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    results_dir = prepare_for_experiment(args, sys.argv[2], sys.argv[1])
    run(sys.argv[1], args)