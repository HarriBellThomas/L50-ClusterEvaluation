#!/usr/bin/env python3
import os
import paramiko
import base64
import time
from scp import SCPClient
import threading

#
def run_remote_setup(source, target, args, id, sleep=True):
    targets = target.split(",")
    if len(targets) > 1:
        threads = []
        for t in targets:
            _t = threading.Thread(target=run_remote_setup, args=[source, t, args, id, sleep])
            _t.start()
            threads.append(_t)
        for _t in threads:
            _t.join()
            return
        
    directory = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists("{}/{}/remote.py".format(directory, source)):
        print("Setting up remote for plan: {}...".format(source))

        encodedArgBytes = base64.b64encode(args.encode("utf-8"))
        encodedArgs = str(encodedArgBytes, "utf-8")
        cmd = "tmux kill-session -t evaluation-{} > /dev/null 2>&1; ".format(id)
        cmd = cmd + "tmux new-session -d -s evaluation-{}; ".format(id)
        cmd = cmd + "tmux send -t evaluation-{} \"python3 ~/x/experiments/{}/remote.py '{}'\" ENTER; ".format(id, source, encodedArgs)
        cmd = cmd + "tmux ls"

        ssh = paramiko.SSHClient()
        ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(target), username='L50', pkey=ssh_key)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))
        ssh.close()

        print("Remote setup complete for plan: {}.\n".format(source))
        if sleep:
            time.sleep(2)
    else:
        print("No remote setup for plan: {}.".format(source))

#
def reset_remote(source, target, id, run, results_dir):
    targets = target.split(",")
    if len(targets) > 1:
        threads = []
        for t in targets:
            _t = threading.Thread(target=reset_remote, args=[source, t, id, run, results_dir])
            _t.start()
            threads.append(_t)
        for _t in threads:
            _t.join()
            return
    
    directory = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists("{}/{}/remote.py".format(directory, source)):
        print("\nResetting evaluation environment for {}...".format(target))
        ssh = paramiko.SSHClient()
        ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(target), username='L50', pkey=ssh_key)
        cmd = "tmux send -t evaluation-{} C-c;".format(id)
        cmd = cmd + "tmux send -t evaluation-{} \"sudo kill -9 $(pidof iperf)\" ENTER;".format(id)
        cmd = cmd + "tmux kill-session -t evaluation-{};".format(id)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))
        
        # Retrieve remote results
        print("Retrieving remote logs...")
        scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x)
        scp.get(
            "/tmp/{}/{}/*".format(id, run), # from remote
            "{}/{}/{}/".format(results_dir, run, target), # to local
            recursive=True, # recursive
            preserve_times=True # preserve_times
        )
        ssh.exec_command("rm -rf /tmp/{}".format(id), get_pty=True)


        ssh.close()
        print("Done.\n")
    else:
        print("No remote environment to reset.")

