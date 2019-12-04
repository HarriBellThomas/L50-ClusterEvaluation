import re

def parse_iperf_local(path, drop_first_n=0, drop_last_n=0):
    return _extract_floats_with_regex(path, "(\d+(?= Mbits\/sec))", drop_first_n, drop_last_n)

def parse_ping_local(path, drop_first_n=0, drop_last_n=0):
    return _extract_floats_with_regex(path, "((?<=time=)\d+.\d+(?= ms))", drop_first_n, drop_last_n)

def _extract_floats_with_regex(path, regex, drop_first_n=0, drop_last_n=0):
    with open(path, "r") as f:
            data = f.read()
            output = re.findall(regex, data)
            return [float(x) for x in output[drop_first_n:(len(output)-drop_last_n)]]