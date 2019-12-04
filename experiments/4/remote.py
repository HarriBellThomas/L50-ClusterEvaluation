#!/usr/bin/env python3
import time
import sys
import os
import json
import base64
import socket
import pathlib


def run_client(target, arguments, results_dir):
    buffer_length = arguments.get('buffer_length', 8000)
    time = arguments.get('time', 5)
    udp = arguments.get('udp', False)
    command = "sudo iperf {} 2>&1 | tee {}/remote".format(
        " ".join([
            "-u" if udp else "",
            "-i 0.5",
            "-t {}".format(time),
            "-f m",
            "-l {}".format(buffer_length),
            "-c {}".format(str(target)),
            "-b 10g"
        ]),
        results_dir
    )
    print(command)
    os.system(command)

    # Then kill server.

def start_server(target, arguments, results_dir):
    udp = arguments.get("udp", False)

    print("Running iperf server...")
    cmd = "sudo iperf {} -s -i 0.5 -f m & >> {}/remote-server".format(
        "-u" if udp else "", 
        results_dir
    )


argsEncodedBytes = base64.b64decode(sys.argv[1].encode("utf-8"))
argsEncodedJson = str(argsEncodedBytes, "utf-8")
args = json.loads(argsEncodedJson)

path = pathlib.Path("/tmp/{}/{}".format(args.get("_id"), args.get("_run")))
path.mkdir(parents=True, exist_ok=True)
results_dir = path.absolute().as_posix()
os.system("echo '{}' > ~/test".format(results_dir))

start_server(args["_origin"], args, results_dir)
# time.sleep(2)
# run_client(args["_origin"], args, results_dir)