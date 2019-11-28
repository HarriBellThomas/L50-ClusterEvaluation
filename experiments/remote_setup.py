#!/usr/bin/env python3
import os
import paramiko
import base64
import time
from scp import SCPClient

#
def run_remote_setup(exp_num, target, args, id):
    directory = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists("{}/{}/remote.py".format(directory, exp_num)):
        print("Setting up remote for experiment {}...".format(exp_num))

        encodedArgBytes = base64.b64encode(args.encode("utf-8"))
        encodedArgs = str(encodedArgBytes, "utf-8")
        cmd = "tmux kill-session -t evaluation-{} > /dev/null 2>&1; ".format(id)
        cmd = cmd + "tmux new-session -d -s evaluation-{}; ".format(id)
        cmd = cmd + "tmux send -t evaluation-{} \"python3 ~/x/experiments/{}/remote.py '{}'\" ENTER; ".format(id, exp_num, encodedArgs)
        cmd = cmd + "tmux ls"

        ssh = paramiko.SSHClient()
        ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(target), username='L50', pkey=ssh_key)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))
        ssh.close()

        print("Remote setup complete for experiment {}.\n".format(exp_num))
        time.sleep(2)
    else:
        print("No remote setup for experiment {}.".format(exp_num))

#
def reset_remote(exp_num, target, id, run, results_dir):
    directory = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists("{}/{}/remote.py".format(directory, exp_num)):
        print("\nResetting evaluation environment for {}...".format(target))
        ssh = paramiko.SSHClient()
        ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(target), username='L50', pkey=ssh_key)
        cmd = "tmux send -t evaluation-{} C-c; sleep 2; ".format(id)
        cmd = cmd + "tmux kill-session -t evaluation-{};".format(id)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))
        
        # Retrieve remote results
        print("Retrieving remote logs...")
        scp = SCPClient(ssh)
        scp.get(
            "/tmp/{}/{}/remote".format(id, run), # from remote
            "{}/{}/remote".format(results_dir, run), # to local
            recursive=False, # recursive
            preserve_times=True # preserve_times
        )


        ssh.close()
        print("Done.\n")
    else:
        print("No remote environment to reset.")

