#!/usr/bin/env python3
import argparse
import os
import time
import pathlib
import socket
from IPy import IP
import uuid


#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distribute experiments.')
    parser.add_argument('-e','--experiment', help='Which experiment to run. Omit to run all.', default=0)
    parser.add_argument('-t','--target', help='Target IP addresses.', required=True)
    parser.add_argument('-l','--lmk', help='Email to notify when done.', default=False)
    args = parser.parse_args()

    # Ensure results path exists.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = pathlib.Path("{}/results".format(script_dir))
    path.mkdir(parents=True, exist_ok=True)
    results_dir = path.absolute().as_posix()

    distribution_num = 0
    while(pathlib.Path("{}/results/{}".format(script_dir, "d{}".format(distribution_num))).exists()):
        distribution_num = distribution_num + 1

    _id = str(uuid.uuid4())
    d_path = pathlib.Path("{}/results/{}".format(script_dir, "d{}".format(distribution_num)))
    d_path.mkdir(parents=True, exist_ok=True)
    distribution_dir = d_path.absolute().as_posix()
    print("ID: d{} ({})".format(distribution_num, _id))
    print(distribution_dir)
    
    my_ip = str(socket.gethostbyname(socket.gethostname()))
    pathlib.Path("{}/results/{}/{}".format(script_dir, "d{}".format(distribution_num), my_ip)).mkdir(parents=True, exist_ok=True)

    targets = []
    for t in args.target.split(","):
        if t != my_ip:
            try:
                ip = IP(t)
                targets.append(t)
                pathlib.Path("{}/results/{}/{}".format(script_dir, "d{}".format(distribution_num), t))
            except ValueError:
                print("Invalid IP address: {}".format(t))
                print("Aborted")
                exit(1)
    print("Targets: {}".format(targets))

    # The plan: actual experiments are run by distribute_client.py.
    # Run here first then send to targets in turn.


    # python3 distribute_client.py /tmp/path 10.0.0.4,10.0.0.5 
    os.system("python3 {}/distribute_client.py {} {} {} {} {} {}".format(
        script_dir,
        "-e {}".format(args.experiment), # Experiments to run.
        "-t {}".format(",".join([my_ip, *targets])), # Target IPs.
        "-o {}".format(my_ip),
        "-d {}".format(distribution_dir),
        "-r {}".format(",".join(targets)),
        "-i {}".format(_id)
    ))