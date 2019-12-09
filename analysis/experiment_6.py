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
from helpers.parse import parse_ping_local, parse_iperf_local, parse_multi_client_iperf_server, parse_iperf_local_sum
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
def experiment_6(experiment_data, dist_uri, name_mapping):
    experiment = "experiment-6"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()
    data = collect_data(experiment_data, dist_uri, experiment)
    hosts = [x.split("/")[-1] for x in glob.glob("{}/*".format(dist_uri))]

    # Do stuff with data.
    mapped_hosts = [h for h in hosts if h != "vis"]

    for host in mapped_hosts:
        for exp in data[host]:
            for combination in data[host][exp]:
                to_plot = data[host][exp][combination]

                length = min([len(x) for x in to_plot["locals"]])
                xs = [0.5*i for i in range(0, length)]
                
                fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6, 4), sharex=False, sharey=True)
                axes.margins(x=0)
                axes.set_ylim(0, 1100)
                axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
                axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

                for local in to_plot["locals"]:
                    axes.plot(xs, local[0:length], 'k-', color="green", alpha=0.6)

                
                min_length = 10000
                for remote in to_plot["remotes"]:
                    _r = remote[0:length]
                    axes.plot([x+0.01 for x in xs][0:len(_r)], _r, 'k-', color="red", alpha=0.6)
                    min_length = min(min_length, len(_r))

                combined = []
                for _r in range(0, min_length):
                    combined.append(sum([float(to_plot["remotes"][x][_r]) for x in range(0, len(to_plot["remotes"]))]))
                axes.plot([x+0.02 for x in xs][0:len(combined)], combined, 'k-', color="blue", alpha=0.6)


                plt.savefig("{}/vis-7-{}-{}.png".format(output, name_mapping[host], combination), dpi=dpi)
                print("{}/vis-7-{}-{}.png".format(output, name_mapping[host], combination))
                plt.close(fig)


######
def experiment_6_aggregated(output, experiment_data, dist_uris, name_mapping):
    experiment = "experiment-6"
    data = {}
    for dist_uri in dist_uris:
        _d = collect_data(experiment_data, dist_uri, experiment)
        for host in _d:
            if host not in data:
                data[host] = []
            data[host].append(_d[host])
    
    # Ugh here we go...
    num_host_data = {}
    # num_host_data[host][num][remotes|locals]
    for host in data:
        num_host_data[host] = {}
        for _n in range(0, 4):
            num_host_data[host][_n] = []

        for data_collection in data[host]:
            for experiment in data_collection:
                for num_hosts in data_collection[experiment]:
                    _host_exp_data = data_collection[experiment][num_hosts]
                    num_host_data[host][experiment].append(_host_exp_data)


    results = {}
    for host in num_host_data:
        results[host] = {}
        for experiment in num_host_data[host]:
            _d = num_host_data[host][experiment]
            _lengths = {
                "remotes": 10000,
                "locals": 10000,
            }
            for dist in _d:
                _lengths["remotes"] = min(_lengths["remotes"], *[len(i) for i in dist["remotes"]])
                _lengths["locals"] = min(_lengths["locals"], *[len(i) for i in dist["locals"]])

            _types = ["locals", "remotes"]
            _results = {
                "data": {},
                "errors": {}
            }
            for _type in _types:
                _results["data"][_type] = []
                _results["errors"][_type] = []
                paired = [_dist[_type] for _dist in _d]
                 
                num_clients = (experiment % 4) + 1            
                for i in range(0, num_clients if _type == "locals" else 1): 
                    _results["data"][_type].append([])
                    _results["errors"][_type].append([])

                    for j in range(0, _lengths[_type]):
                        _timestep = ([x[i] for x in paired])
                        timestep = [x[j] for x in _timestep]
                        _results["data"][_type][i].append(np.mean(timestep))
                        _results["errors"][_type][i].append(np.std(timestep))
            
            results[host][experiment] = _results
            to_plot = _results["data"]
            
            length = min(
                min([len(x) for x in to_plot["locals"]]),
                min([len(x) for x in to_plot["remotes"]])
            )
            xs = [0.5*i for i in range(0, length)]

            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6, 4), sharex=False, sharey=True)
            axes.margins(x=0)
            axes.set_ylim(0, 1100)
            axes.set_ylabel("$Bandwidth\ (Mbps)$", fontsize=14)
            axes.set_xlabel("$Time\ (seconds)$", fontsize=14)

            for i in range(0, len(to_plot["locals"])):
                local = _results["data"]["locals"][i][0:length]
                err = _results["errors"]["locals"][i][0:length]
                _xs, _ys, _errs = generate_spline(xs, local, err)
                axes.plot(_xs, _ys, 'k-', color="green", alpha=0.6)
                axes.fill_between(_xs, _ys-_errs, _ys+_errs, alpha=0.15, color='green')

            min_length = 10000
            for i in range(0, len(to_plot["remotes"])):
                remote = _results["data"]["remotes"][i][0:length]
                err = _results["errors"]["remotes"][i][0:length]
                _xs, _ys, _errs = generate_spline([x+0.01 for x in xs][0:len(remote)], remote, err)
                axes.plot(_xs, _ys, 'k-', color="red", alpha=0.6)
                min_length = min(min_length, len(remote))
                axes.fill_between(_xs, _ys-_errs, _ys+_errs, alpha=0.15, color='red')

            
            plt.savefig("{}/aggr-vis-9-{}-{}.png".format(output, name_mapping[host], (experiment%4)+1), dpi=dpi)
            print("{}/aggr-vis-9-{}-{}.png".format(output, name_mapping[host], (experiment%4)+1))
            plt.close(fig)


#
def collect_data(experiment_data, dist_uri, experiment):
    # Get data.
    experiments = range(0, 4)
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
                t = to_hosts[0]

                locals = glob.glob("{}/local-*".format(t))
                if(len(locals) > 1):
                    experiment_data[len(locals)] = {
                        "remotes": [parse_iperf_local_sum("{}/remote".format(t), 6)],
                        "locals": [parse_iperf_local(l, 6) for l in locals]
                    }
                else:
                    experiment_data[1] = {
                        "remotes": [parse_iperf_local("{}/remote".format(t), 6)],
                        "locals": [parse_iperf_local(l, 6) for l in locals]
                    }
                
                data[host][i] = experiment_data
    return data


#
def generate_spline(xs, ys, errs):
    ys = np.array(ys)
    err = np.array(errs)

    x_vals = np.array(xs)
    xnew = np.linspace(x_vals.min(), x_vals.max(), 300) 
    spl = make_interp_spline(x_vals, ys, k=2)  # type: BSpline
    spl_err = make_interp_spline(x_vals, err, k=2)  # type: BSpline
    ys_smooth = spl(xnew)
    err_smooth = spl_err(xnew)

    return xnew, ys_smooth, err_smooth


#
def pairwise_sum(l1, l2):
    length = min(len(l1), len(l2))
    return [sum(x) for x in zip(list1[0:length], list2[0:length])]


#
def mean(a):
    return sum(a) / len(a)
