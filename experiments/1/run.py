#!/usr/bin/env python3
import argparse
import sys
import os
sys.path.insert(1, "{}/..".format(os.path.dirname(os.path.abspath(__file__))))
import json
from experiment import prepare_for_experiment

def run(target, arguments, results_dir):
    buffer_length = arguments.get('buffer_length', 80000)
    time = arguments.get('time', 5)
    os.system("iperf -i 1 -t {} -f m -c {} -l {} 2>&1 | tee {}/local".format(
        time, str(target), buffer_length, results_dir
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    results_dir = prepare_for_experiment(args, sys.argv[2], sys.argv[1])
    run(sys.argv[1], args, results_dir)