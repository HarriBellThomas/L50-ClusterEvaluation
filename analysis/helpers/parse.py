import re

def parse_iperf_local(path, drop_first_n=0):
    with open(path, "r") as f:
        data = f.read()
        output = re.findall("(\d+(?= Mbits\/sec))", data)
        return [float(x) for x in output[drop_first_n:]]


def parse_ping_local(path, drop_first_n=0):
    with open(path, "r") as f:
        data = f.read()
        output = re.findall("((?<=time=)\d+.\d+(?= ms))", data)
        return [float(x) for x in output[drop_first_n:]]