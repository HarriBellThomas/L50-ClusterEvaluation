#!/usr/bin/env python3
import sys
import os
from os.path import dirname, abspath
sys.path.insert(1, "{}/analysis/helpers".format(dirname(dirname(dirname(abspath(__file__))))))
import glob
from parse import parse_iperf_local

input = sys.argv[1]
output = sys.argv[2]

# temp hack
_parts = input.split("/")
_uuid = _parts[len(_parts) - 1]

parameter_sets = glob.glob("{}/{}/*".format(input, _uuid))
for param_set in parameter_sets:
    targets = glob.glob("{}/*".format(param_set))
    for t in targets:
        if os.path.isdir(t):
            print("\n")
            print(t)
            print("ping -> {}: {}".format(t.split("/")[-1], parse_iperf_local("{}/local".format(t))))
    

# print("{} -> {}".format(input, output))
# parse_iperf_local("{}/local".format(input))