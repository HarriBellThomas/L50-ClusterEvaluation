#!/usr/bin/env python3
import argparse
import sys
import os

def run(target):
   os.system("iperf -t 5 -f m -c {}".format(str(target))) 


if __name__ == "__main__":
    run(sys.argv[1])