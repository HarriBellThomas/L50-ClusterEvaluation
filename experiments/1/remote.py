#!/usr/bin/env python3
import time
import sys
import os
import json
import base64
import socket
import pathlib


argsEncodedBytes = base64.b64decode(sys.argv[1].encode("utf-8"))
argsEncodedJson = str(argsEncodedBytes, "utf-8")
args = json.loads(argsEncodedJson)

path = pathlib.Path("/tmp/{}/{}".format(args.get("_id"), args.get("_run")))
path.mkdir(parents=True, exist_ok=True)
results_dir = path.absolute().as_posix()

print("Running iperf...")
os.system("iperf -s -i 1 -f m >> {}/remote".format(results_dir))