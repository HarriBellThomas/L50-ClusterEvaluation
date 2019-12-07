#!/usr/bin/env python3
import time
import sys
import os
import json
import base64
import socket
import pathlib
import socket

def run_client(target, arguments, results_dir, i=0):
    pass

argsEncodedBytes = base64.b64decode(sys.argv[1].encode("utf-8"))
argsEncodedJson = str(argsEncodedBytes, "utf-8")
args = json.loads(argsEncodedJson)

path = pathlib.Path("/tmp/{}/{}".format(args.get("_id"), args.get("_run")))
path.mkdir(parents=True, exist_ok=True)
results_dir = path.absolute().as_posix()

victims = args["_victims"]
print(victims)
print(str(socket.gethostbyname(socket.gethostname())))
index = victims.split(",").index(
    str(socket.gethostbyname(socket.gethostname()))
)
print(index)

time.sleep(3)
run_client(args["_origin"], args, results_dir, index)