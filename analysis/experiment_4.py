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
def experiment_4(experiment_data, dist_uri, name_mapping, cross=False):
    experiment = "experiment-4" if not cross else "experiment-4-crosstalk"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()

    # Get data.
    experiments = range(0, len(experiment_data[4]["parameters"]))
    hosts = [x.split("/")[-1] for x in glob.glob("{}/*".format(dist_uri))]
    data = {}
    for host in hosts:
        if host == "vis":
            continue
        data[name_mapping[host]] = {}
        experiment_folder_name = glob.glob("{}/{}/*-{}".format(dist_uri, host, experiment))
        if len(experiment_folder_name) > 0:
            experiment_folder_name = experiment_folder_name[0]
            for i in experiments:
                data[name_mapping[host]][i] = {}
                to_hosts = glob.glob("{}/{}/*".format(experiment_folder_name, i))
                to_hosts.sort()
                for t in to_hosts:
                    if os.path.isdir(t):
                        target = t.split("/")[-1]
                        data[name_mapping[host]][i][name_mapping[target]] = (
                            parse_iperf_local("{}/local".format(t), 6), # host out
                            parse_iperf_local("{}/local-server".format(t), 6), # host in
                            parse_iperf_local("{}/remote".format(t), 6), # target out
                            parse_iperf_local("{}/remote-server".format(t), 6) # target in
                        )
    
    # Do stuff with data.
    mapped_hosts = [name_mapping[h] for h in hosts if h != "vis"]

    # Average of all per host.
    combined = {}
    for exp in experiments:
        combined[exp] = {}
        egress_data = {}
        ingress_data = {}
        for host in mapped_hosts:
            egress_data[host] = []
            ingress_data[host] = []

        for host in mapped_hosts:
            for target in mapped_hosts:
                if target != host:
                    egress_data[host].append(data[host][exp][target][0])
                    ingress_data[host].append(data[host][exp][target][1 if exp == 0 else 2])
                    egress_data[target].append(data[host][exp][target][2])
                    ingress_data[target].append(data[host][exp][target][3 if exp == 0 else 0])
        
        # Calc timestep average
        for host in mapped_hosts:
            egress = True
            combined[exp][host] = {}

            # Individual
            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6, 4), sharex=False, sharey=True)
            axes.margins(x=0)
            axes.set_ylim(0, 1100)
            axes.set_xlim(0, 22)
            axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
            axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

            length = min(
                min([len(x) for x in egress_data[host]]),
                min([len(x) for x in ingress_data[host]])
            )
            for dataset in [egress_data[host], ingress_data[host]]:
                averaged_mean = []
                averaged_std = []
                for i in range(0, length): # each timestep
                    zipped_datapoints = [dataset[j][i] for j in range(0, len(dataset))]
                    averaged_mean.append(np.mean(zipped_datapoints))
                    averaged_std.append(np.std(zipped_datapoints))

                ys = np.array(averaged_mean)
                err = np.array(averaged_std)

                x_vals = np.array([1*i for i in range(0, len(averaged_mean))])
                xnew = np.linspace(x_vals.min(), x_vals.max(), 300) 

                spl = make_interp_spline(x_vals, ys, k=2)  # type: BSpline
                spl_err = make_interp_spline(x_vals, err, k=2)  # type: BSpline
                ys_smooth = spl(xnew)
                err_smooth = spl_err(xnew)

                axes.plot(xnew, ys_smooth, 'k-', color=("darkblue" if egress else "darkred"), alpha=0.6)
                axes.fill_between(xnew, ys_smooth-err_smooth, ys_smooth+err_smooth, color=("darkblue" if egress else "darkred"), alpha=0.3)
                
                combined[exp][host][0 if egress else 1] = (xnew, ys_smooth, err_smooth)
                egress = False
            
            axes.tick_params(axis='y', which='minor', bottom=False)
            axes.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
            axes.grid(b=True, which='major', linestyle='-', axis='y', alpha=0.3)
            axes.grid(b=True, which='minor', linestyle='-', axis='y', alpha=0.2)
            plt.savefig("{}/vis-5-{}-{}{}.png".format(output, host, exp, "-crosstalk" if cross else ""), dpi=dpi)
            print("{}/vis-5-{}-{}{}.png".format(output, host, exp, "-crosstalk" if cross else ""))
            plt.close(fig)

    
    # Combined graphs.
    for host in mapped_hosts:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6, 4), sharex=False, sharey=True)
        axes.margins(x=0)
        axes.set_ylim(0, 1100)
        axes.set_xlim(0, 22)
        axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
        axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

        # egress, tcp
        d = combined[0][host][0]
        axes.plot(d[0], d[1], 'k-', color="darkblue", alpha=0.6, label="$TCP\ Egress$")
        axes.fill_between(d[0], d[1]-d[2], d[1]+d[2], color="darkblue", alpha=0.3)

        # ingress, tcp
        d = combined[0][host][1]
        axes.plot(d[0], d[1], 'k-', color="darkred", alpha=0.6, label="$TCP\ Ingress$")
        axes.fill_between(d[0], d[1]-d[2], d[1]+d[2], color="darkred", alpha=0.3)

        # egress, udp
        d = combined[1][host][0]
        axes.plot(d[0], d[1], 'k-', color="orange", alpha=0.6, label="$UDP\ Egress$")
        axes.fill_between(d[0], d[1]-d[2], d[1]+d[2], color="orange", alpha=0.3)

        # ingress, udp
        d = combined[1][host][1]
        axes.plot(d[0], d[1], 'k-', color="green", alpha=0.6, label="$UDP\ Ingress$")
        axes.fill_between(d[0], d[1]-d[2], d[1]+d[2], color="green", alpha=0.3)

        axes.tick_params(axis='y', which='minor', bottom=False)
        axes.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        axes.grid(b=True, which='major', linestyle='-', axis='y', alpha=0.3)
        axes.grid(b=True, which='minor', linestyle='-', axis='y', alpha=0.2)
        axes.legend(loc='lower center', ncol=2, fancybox=True, shadow=True, edgecolor='black')
        plt.savefig("{}/vis-5-{}-{}{}.png".format(output, host, 'combined', "-crosstalk" if cross else ""), dpi=dpi)
        print("{}/vis-5-{}-{}{}.png".format(output, host, 'combined', "-crosstalk" if cross else ""))
        plt.close(fig)    
