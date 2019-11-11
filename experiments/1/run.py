#!/usr/bin/env python3
import argparse
import sys

def run(ssh_pswd):
    print("test {}".format(ssh_pswd))


if __name__ == "__main__":
    run(sys.argv[1])