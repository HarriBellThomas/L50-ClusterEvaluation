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


def parse_multi_client_iperf_server(path):
    with open(path, "r") as f:
        data = f.read()
        output = re.findall("(\[\s*\d+\].*)", data) # Get only relevant lines
        outputs = [x for x in output if "connected" not in x] # Removed 'connected from...' lines
        client_numbers = [x.strip() for x in re.findall("((?<=\n\[)\s*\d+(?=\].*))", data)]

        timestep = 0
        timestep_bandwidths = [[]]
        clients_seen = []
        for i in range(0, len(client_numbers)):
            if client_numbers[i] in clients_seen:
                timestep = timestep + 1
                clients_seen = []
                timestep_bandwidths.append([])

            clients_seen.append(client_numbers[i])
            bw = re.findall("(\d+\.\d+(?= Mbits\/sec))", output[i])
            if len(bw) > 0 :
                timestep_bandwidths[timestep].append(float(bw[0]))
            
        return timestep_bandwidths