import paramiko
def crosstalk(host1, host2, bandwidth, time):
    server_command = "iperf3 -s {}".format(str(host1))
    client_command = "iperf3 -c {} -b {} -t {}".format(str(host2), bandwidth, time)
    tmux_command = "tmux new-session -d -s evaluation-crosstalk; tmux send -t evaluation-crosstalk \"{}\" ENTER; tmux ls;"
    run_remote_command(host1, tmux_command.format(server_command))
    run_remote_command(host1, tmux_command.format(client_command))

def stop_crosstalk(host1, host2):
    stop_crosstalk(host1)
    stop_crosstalk(host2)

def stop_crosstalk(host):
    cmd = "tmux send -t evaluation-crosstalk C-c; sleep 2; tmux kill-session -t evaluation-crosstalk;"
    run_remote_command(host, cmd)

def run_remote_command(host, cmd):
    ssh = paramiko.SSHClient()
    ssh_key = paramiko.RSAKey.from_private_key_file("/home/L50/.ssh/evaluation")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(str(host), username='L50', pkey=ssh_key)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)
    print("stdout:  " + str(ssh_stdout.read()))
    print("stderr:  " + str(ssh_stderr.read()))
    ssh.close()