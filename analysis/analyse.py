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
from helpers.parse import parse_ping_local, parse_iperf_local
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import string
from sklearn.preprocessing import normalize
from scipy.interpolate import make_interp_spline, BSpline


# plt.rcParams['figure.dpi'] = 600 
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{libertine}\usepackage[libertine]{newtxmath}\usepackage{sfmath}\usepackage[T1]{fontenc}'
# plt.rcParams['figure.figsize'] = 8, 4

colourmap = {
    "vm0": "green", "vm1":"red", "vm2":"orange", "vm3":"darkblue", "vm4":"purple"
}

#
def visualise_experiments(definitions, data_path):
    parent_directory = dirname(dirname(os.path.abspath(__file__)))
    for key in definitions:
        paths_to_parse = glob.glob("{}/**/*-experiment-{}".format(data_path, key))
        for path in paths_to_parse:
            path_parts = path.split("/")
            output_path = pathlib.Path("{}/vis/experiment-{}/{}".format(data_path, key, path_parts[len(path_parts)-2]))
            output_path.mkdir(parents=True, exist_ok=True)
            visualisation_script = pathlib.Path("{}/experiments/{}/visualise.py".format(parent_directory, definitions[key]["src"]))
            if visualisation_script.exists():
                os.system("python3 {} {} {}".format(
                    visualisation_script.absolute().as_posix(),
                    path,
                    output_path.absolute().as_posix()
                ))
            else:
                print("Can't find visualisation script")



#
def plot_ping_topology(experiment_data, dist_uri, name_mapping, color='darkblue'):


    experiment = "experiment-2"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()
    print()
    hosts = [x.split("/")[-1] for x in glob.glob("{}/*".format(dist_uri))]
    data = {}
    for host in hosts:
        if host == 'vis':
            continue
        data[name_mapping[host]] = {}
        experiment_folder_name = glob.glob("{}/{}/*-{}".format(dist_uri, host, experiment))
        if len(experiment_folder_name) > 0:
            experiment_folder_name = experiment_folder_name[0]
            experiments = range(0, len(experiment_data[2]["parameters"]))
            for i in experiments:
                data[name_mapping[host]][i] = []
                to_hosts = glob.glob("{}/{}/*".format(experiment_folder_name, i))
                to_hosts.sort()
                for t in to_hosts:
                    if os.path.isdir(t):
                        target = t.split("/")[-1]
                        data[name_mapping[host]][i].append(parse_ping_local("{}/local".format(t)))

    

    fs = 10  # fontsize
    pos = [0, 1, 2, 3]

    fig, axes = plt.subplots(nrows=5, ncols=4, figsize=(8, 10), sharex=False, sharey=True)
    i = 0
    param_sets = [0,2,4,6]
    keys = (list(data.keys()))
    keys.sort()

    rows = ['${}$ '.format(row) for row in keys]
    for host in keys:
        j = 0
        vm_names = [x for x in keys if x != host]
        for param_set in param_sets:
            parts = axes[i, j].violinplot(
                data[host][param_set], pos, points=60, widths=0.6, showmeans=False, showextrema=True, showmedians=True
            )
            k = 0
            for vp in parts['bodies']:
                vp.set_facecolor(colourmap[vm_names[k]])
                vp.set_edgecolor(colourmap[vm_names[k]])
                vp.set_linewidth(1)
                vp.set_alpha(0.8) 
                k = k + 1     
            for partname in ('cbars','cmins','cmaxes','cmedians'): # cmeans
                vp = parts[partname]
                vp.set_edgecolor('black')
                vp.set_linewidth(1)  
                vp.set_alpha(0.5)        
                        
            
            axes[i, j].set_ylim([0,8])
            labels = [""] + vm_names
            axes[i, j].set_xticklabels(labels)
            axes[i, j].tick_params(axis='y', which='minor', bottom=False)
            axes[i, j].grid(b=True, which='major', linestyle='--', axis='y')
            axes[i, j].grid(b=True, which='minor', linestyle='--', axis='y')

            if j != 0:
                pass
                # axes[i, j].yaxis.set_visible(False)
            else:
                axes[i, j].set_ylabel("RTTs ($ms$)", fontsize=10)
            if i == 0:
                axes[i, j].set_title("Interval\n{}".format(["0.1s", "0.01s", "0.001s", "0.0001s"][j]), fontsize=fs)
            
            j = j + 1
        i = i + 1

    pad = 5 # in points
    for ax, row in zip(axes[:,0], rows):
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                xycoords=ax.yaxis.label, textcoords='offset points',
                size='x-large', ha='right', va='center')

    for ax in axes.flat:
        ax.xaxis.set_major_locator(plt.MaxNLocator(4))
        ax.yaxis.set_major_locator(plt.MaxNLocator(3))
        ax.yaxis.set_minor_locator(plt.MaxNLocator(8))
    #     ax.set_yticklabels([])

    fig.subplots_adjust(hspace=0.3, wspace=0.1, top=0.95, right=0.98, bottom=0.05)
    plt.savefig("{}/out2.png".format(output), dpi=600)


    # Now make a relative distance plot
    param_set = 2
    distances = []
    for host in keys:
        host_distances = []
        _i = 0
        for target in keys:
            if target == host:
                host_distances.append(0)
            else:
                host_distances.append(
                    np.median(data[host][param_set][_i])
                )
                _i = _i + 1
  
        distances.append(host_distances)

    plt.clf()
            
    
    dt = [('len', float)]

    # Do some fixing
    prefer_ltr = True
    new_distances = distances[:]
    for i in range(0,5):
        for j in range(0,5):
            if i >= j:
                new_distances[i][j] = distances[i][j] if prefer_ltr else distances[j][i]
                new_distances[j][i] = distances[i][j] if prefer_ltr else distances[j][i]


    average = np.median([np.mean([i for i in x if i != 0]) for x in new_distances])
    A = np.power(np.array([tuple(x) for x in new_distances]) / average, 3)
    print(A)

    G = nx.from_numpy_matrix(A)
    G = nx.relabel_nodes(
        G, dict(zip(range(len(G.nodes())), keys))
    )    


    G = nx.drawing.nx_agraph.to_agraph(G)
    pos = nx.spring_layout(G, iterations=200)
    plt.figure(figsize=(8,8), tight_layout=False) 
    nx.draw(G, pos, with_labels=True, font_color='white', node_size=8000, font_size=40, font_family='Palatino', width=4, edge_color=color, node_color=color, font_weight='bold')
    plt.margins(0.2)
    plt.savefig("{}/out.png".format(output), dpi=600, pad_inches=3.5)
    # G.draw('/tmp/out.dot', format='dot', prog='neato')


#
def plot_iperf_results(experiment_data, dist_uri, name_mapping):
    experiment = "experiment-1"
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
        
        plt.savefig("{}/out3-{}.png".format(output, exp), dpi=600)


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

            plt.savefig("{}/out4-{}-{}.png".format(output, host, "large" if exp_pair[0]==0 else "small"), dpi=600)




#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse experiments.')
    parser.add_argument('-p','--path', help='Which distribution to analyse.', required=True)
    parser.add_argument('-c','--cluster', help='Cluster number.', default=1)
    args = parser.parse_args()

    # Get experiment definitions.
    directory = dirname(dirname(os.path.abspath(__file__)))
    experiment_data = {}
    with open("{}/experiments/definitions.yml".format(directory), 'r') as stream:
        data = yaml.safe_load(stream)
        if 'experiments' in data:
            for item in data['experiments']:
                if 'id' in item:
                    experiment_data[item['id']] = item

    dist_path = pathlib.Path(args.path)
    dist_uri = dist_path.absolute().as_posix()

    cluster1_mapping = {"10.0.0.4":"vm0", "10.0.0.6":"vm1", "10.0.0.7":"vm2", "10.0.0.8":"vm3", "10.0.0.5":"vm4"}
    cluster2_mapping = {"10.0.0.6":"vm0", "10.0.0.5":"vm1", "10.0.0.4":"vm2", "10.0.0.8":"vm3", "10.0.0.7":"vm4"}

    if dist_path.exists():
        # visualise_experiments(experiment_data, dist_uri)
        if int(args.cluster) == 1:
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, 'darkblue')
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping)
        elif int(args.cluster) == 2:
            plot_ping_topology(experiment_data, dist_uri, cluster2_mapping, 'darkred')
            plot_iperf_results(experiment_data, dist_uri, cluster2_mapping)
        else:
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, 'orange')
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping)

    else: 
        print("Path doesn't exist.")

