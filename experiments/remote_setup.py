#!/usr/bin/env python3
import os
import paramiko

#
def run_remote_setup(exp_num, target, pswd):
    directory = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists("{}/{}/remote.py".format(directory, exp_num)):
        print("Setting up remote for experiment {}...".format(exp_num))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(str(target), username='L50', password=pswd)
        cmd = "tmux kill-session -t evaluation > /dev/null 2>&1; "
        cmd = cmd + "tmux new-session -d -s evaluation; "
        cmd = cmd + "tmux send -t evaluation python3 ~/L50-ClusterEvaluation/experiments/{}/remote.py ENTER".format(exp_num)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
        print("stdout:  " + str(ssh_stdout.read()))
        print("stderr:  " + str(ssh_stderr.read()))

        print("Remote setup complete for experiment {}.\n".format(exp_num))
    else:
        print("No remote setup for experiment {}.".format(exp_num))

#
def reset_remote(target, pswd):
    print("Resetting evaluation environment for {}...".format(target))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(str(target), username='L50', password=pswd)
    cmd = "tmux kill-session -t evaluation;"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
    print("stdout:  " + str(ssh_stdout.read()))
    print("stderr:  " + str(ssh_stderr.read()))

    print("Done.\n")
