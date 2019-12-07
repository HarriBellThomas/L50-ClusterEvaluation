#!/usr/bin/env python3
import argparse
import os
from os.path import dirname
import time
import pathlib
import socket
from IPy import IP
import uuid
import glob
import yaml
from helpers.parse import parse_ping_local, parse_iperf_local, parse_multi_client_iperf_server
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz
import string
from sklearn.preprocessing import normalize
from scipy.interpolate import make_interp_spline, BSpline

plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{libertine}\usepackage[libertine]{newtxmath}\usepackage{sfmath}\usepackage[T1]{fontenc}'
colourmap = {"vm0": "green", "vm1":"red", "vm2":"orange", "vm3":"darkblue", "vm4":"purple"}
dpi = 600
cluster1_mapping = {"10.0.0.4":"vm0", "10.0.0.6":"vm1", "10.0.0.7":"vm2", "10.0.0.8":"vm3", "10.0.0.5":"vm4"}
cluster2_mapping = {"10.0.0.6":"vm0", "10.0.0.5":"vm1", "10.0.0.4":"vm2", "10.0.0.8":"vm3", "10.0.0.7":"vm4"}


######################################################################
def experiment_5(experiment_data, dist_uri, name_mapping):
    experiment = "experiment-5"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()

    # Get data.
    experiments = range(0, len(experiment_data[5]["parameters"] * 4))
    hosts = [x.split("/")[-1] for x in glob.glob("{}/*".format(dist_uri))]
    data = {}
    for host in hosts:
        if host == "vis":
            continue
        data[host] = {}
        experiment_folder_name = glob.glob("{}/{}/*-{}".format(dist_uri, host, experiment))
        if len(experiment_folder_name) > 0:
            experiment_folder_name = experiment_folder_name[0]
            for i in experiments:
                experiment_data = {}
                to_hosts = glob.glob("{}/{}/10*".format(experiment_folder_name, i))
                to_hosts.sort()
                for t in to_hosts:
                    if os.path.isdir(t):
                        if len(to_hosts) == 1:
                            # this is a 1-1 test
                            target = t.split("/")[-1]
                            experiment_data[1] = {
                                "locals": [parse_iperf_local("{}/local-0".format(t), 2)],
                                "remotes": [
                                    parse_iperf_local("{}/remote-{}".format(t, target), 2)
                                ]
                            }

                        else:
                            # this is an n-1 test
                            n = len(to_hosts) - 1
                            if n not in experiment_data:
                                experiment_data[n] = {}

                            target = t.split("/")[-1]
                            seq_parts = target.split(",")
                            if len(seq_parts) > 1:
                                experiment_data[n]["locals"] = []
                                for y in range(0, n):
                                    experiment_data[n]["locals"].append(parse_iperf_local("{}/local-{}".format(t, y), 2))
                                # experiment_data[n]["local"] = [sum(x) for x in parse_multi_client_iperf_server("{}/local".format(t))]
                            else:
                                if not "remotes" in experiment_data[n]:
                                    experiment_data[n]["remotes"] = []
                                experiment_data[n]["remotes"].append(parse_iperf_local("{}/remote-{}".format(t, target), 2))
                

                data[host][i] = experiment_data

    # Do stuff with data.
    mapped_hosts = [h for h in hosts if h != "vis"]

    for host in mapped_hosts:
        for exp in data[host]:
            for combination in data[host][exp]:
                # print("{}, experiment {} -> {} to 1".format(host, exp, combination))
                to_plot = data[host][exp][combination]
                # print(to_plot)
                # print(to_plot["locals"])
                # print(to_plot["remotes"])
                # print("")
                
                length = max(
                    max([len(x) for x in to_plot["locals"]]),
                    max([len(x) for x in to_plot["remotes"]])
                )
                xs = [0.5*i for i in range(0, length)]

                fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6, 4), sharex=False, sharey=True)
                axes.margins(x=0)
                axes.set_ylim(0, 4100)
                # axes.set_xlim(0, 22)
                axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
                axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

                for local in to_plot["locals"]:
                    axes.plot(xs, local, 'k-', color="green", alpha=0.6)

                min_length = 10000
                for remote in to_plot["remotes"]:
                    axes.plot([x+0.01 for x in xs][0:len(remote)], remote, 'k-', color="red", alpha=0.6)
                    min_length = min(min_length, len(remote))

                combined = []
                for _r in range(0, min_length):
                    combined.append(sum([float(to_plot["remotes"][x][_r]) for x in range(0, len(to_plot["remotes"]))]))
                axes.plot([x+0.02 for x in xs][0:len(combined)], combined, 'k-', color="blue", alpha=0.6)


                plt.savefig("{}/vis-6-{}-{}.png".format(output, name_mapping[host], combination), dpi=dpi)
                print("{}/vis-6-{}-{}.png".format(output, name_mapping[host], combination))
                plt.close(fig)

