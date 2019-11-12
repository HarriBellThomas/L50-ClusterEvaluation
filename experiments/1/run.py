#!/usr/bin/env python3
import argparse
import sys
import os
import json

def run(target, arguments):
    buffer_length = arguments.get('buffer_length', 80000)
    time = arguments.get('time', 5)
    os.system("iperf -i 1 -t {} -f m -c {} -l {}".format(
        time, str(target), buffer_length
    ))


if __name__ == "__main__":
    args = json.loads(sys.argv[2])
    run(sys.argv[1], args)