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



############################################################################
def plot_iperf_results(experiment_data, dist_uri, name_mapping, cross=False):
    experiment = "experiment-1" if not cross else "experiment-1-crosstalk"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()

    experiments = range(0, len(experiment_data[1]["parameters"]))
    hosts = [x.split("/")[-1] for x in glob.glob("{}/*".format(dist_uri))]
    data = {}
    for host in hosts:
        if host == 'vis':
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
                        data[name_mapping[host]][i][name_mapping[target]] = parse_iperf_local("{}/local".format(t), 4)
   
    # all hosts on one graph
    for exp in experiments:
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 4), sharex=False, sharey=True)
        axes.margins(x=0)
        axes.set_ylim(600, 1100)
        axes.set_xlim(0, 25)
        axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
        axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

        for host in data.keys():
            per_host_data = []
            for target in data:
                if target != host:
                    per_host_data.append(data[host][exp][target])
            
            
            # Calc timestep average
            averaged_mean = []
            averaged_std = []
            length = np.array([len(x) for x in per_host_data]).min()
            for i in range(0, length): # each timestep
                zipped_datapoints = [per_host_data[j][i] for j in range(0, len(per_host_data))]
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

            axes.plot(xnew, ys_smooth, 'k-', color=colourmap[host], alpha=0.6)
            axes.fill_between(xnew, ys_smooth-err_smooth, ys_smooth+err_smooth, color=colourmap[host], alpha=0.3)
        
        plt.savefig("{}/vis-3-{}{}.png".format(output, exp, "-crosstalk" if cross else ""), dpi=dpi)
        print("{}/vis-3-{}{}.png".format(output, exp, "-crosstalk" if cross else ""))
        plt.close(fig)

    # tcp vs udp for all hosts
    exp_pairs = [(0,2), (1,3)]
    color_pairs = ['darkblue', 'darkred']
    for host in data:
        for exp_pair in exp_pairs:
            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 4), sharex=False, sharey=True)
            axes.margins(x=0)
            axes.set_ylim(600, 1100)
            axes.set_xlim(0, 25)
            axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
            axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

            results = []
            _i = 0
            for exp in exp_pair:
                per_host_data = []
                for target in data:
                    if target != host:
                        per_host_data.append(data[host][exp][target])

                # Calc timestep average
                averaged_mean = []
                averaged_std = []
                length = np.array([len(x) for x in per_host_data]).min()
                for i in range(0, length): # each timestep
                    zipped_datapoints = [per_host_data[j][i] for j in range(0, len(per_host_data))]
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

                axes.plot(xnew, ys_smooth, 'k-', alpha=0.6, color=color_pairs[_i])
                axes.fill_between(xnew, ys_smooth-err_smooth, ys_smooth+err_smooth, alpha=0.3, color=color_pairs[_i])
                _i = _i + 1

            plt.savefig("{}/vis-4-{}-{}{}.png".format(output, host, "large" if exp_pair[0]==0 else "small", "-crosstalk" if cross else ""), dpi=dpi)
            print("{}/vis-4-{}-{}{}.png".format(output, host, "large" if exp_pair[0]==0 else "small", "-crosstalk" if cross else ""))
            plt.close(fig)

