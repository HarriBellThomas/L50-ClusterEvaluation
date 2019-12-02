import os
hosts = os.environ["HOSTS"]
if hosts:
    os.system("cd ~/x; git pull")
    for host in hosts.split(","):
        os.system("ssh L50@{} 'cd ~/x; git pull' > /dev/null".format(host))
    print("Done")
else:
    print("No hosts")
