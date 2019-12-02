#!/usr/bin/env python3
import argparse
import os
from os.path import dirname, abspath
import time
import pathlib
import socket
from IPy import IP
import uuid
import paramiko
import glob

#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distribution client.')
    parser.add_argument('-e','--experiment', help='Which experiment to run. Omit to run all.', default=0)
    parser.add_argument('-t','--target', help='Target IP addresses.', required=True)
    parser.add_argument('-l','--lmk', help='Email to notify when done.', default=False)
    parser.add_argument('-o','--origin', help='IP of the master node.', required=True)
    parser.add_argument('-d','--origindir', help='Directory to store results on the master.', required=True)
    parser.add_argument('-r','--remaining', help='IPs of the nodes remaining in the queue.', default="")
    parser.add_argument('-i','--uuid', help='UUID to set for this set of experiments.', default=str(uuid.uuid4()))
    args = parser.parse_args()

    my_ip = str(socket.gethostbyname(socket.gethostname()))
    local = args.origin == my_ip
    print("distribute_client for {}...".format(args.uuid))
    print(args)
    print("")

    # Find experiment.py
    script_dir_parent = dirname(dirname(abspath(__file__)))
    experiments_dir_path = pathlib.Path("{}/experiments".format(script_dir_parent))
    experiments_dir = experiments_dir_path.absolute().as_posix()

    # Run experiments.
    _id = args.uuid
    os.system("python3 {}/experiment.py {} {} {}".format(
        experiments_dir,
        "-e {}".format(args.experiment),
        "-t {}".format(args.target),
        "-i {}".format(_id)
    ))

    if local:
        os.system("cp -r {}/results/data/{}-* {}/{}".format(
            experiments_dir, _id, args.origindir, my_ip
        ))
    else:
        to_copy = glob.glob("{}/results/data/{}-*".format(experiments_dir))
        for dir in to_copy:
            print(dir)
            print(os.path.basename(dir))
            os.system("scp -rp {} L50@{}:{}/{}/{}".format(
                dir, args.origin, args.origindir, my_ip, os.path.basename(dir)
            ))
    
    # Invoke next in chain.
    remaining = args.remaining.split(",")
    if(len(remaining[0]) > 0):
        next = remaining.pop(0)
        print("\n\nNext up is {}\n\n".format(next))

        cmd = "tmux kill-session -t dist-evaluation-{} > /dev/null 2>&1; ".format(_id)
        cmd = cmd + "tmux new-session -d -s dist-evaluation-{}; ".format(_id)
        cmd = cmd + "tmux send -t dist-evaluation-{} \"python3 ~/x/distribute/distribute_client.py {}\" ENTER; ".format(
            _id, " ".join([
                "-e {}".format(args.experiment), # Experiments to run.
                "-t {}".format(args.target), # Target IPs.
                "-o {}".format(args.origin),
                "-d {}".format(args.origindir),
                "-r {}".format(",".join(remaining)) if len(remaining) > 0 else "",
                "-i {}".format(_id)
            ])
        )
        cmd = cmd + "tmux ls"

        ssh = paramiko.SSHClient()
        ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(next), username='L50', pkey=ssh_key)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))
        ssh.close()

    else:
        print("No hosts remaining. Terminate here.")

