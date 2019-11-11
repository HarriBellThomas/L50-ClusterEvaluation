#!/usr/bin/env python3
import argparse
import sys
import os

def run(target):
   os.system("iperf -t 10 -c {}".format(str(target))) 


if __name__ == "__main__":
    run(sys.argv[1])