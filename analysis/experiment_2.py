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


##############################################################################################
def plot_ping_topology(experiment_data, dist_uri, name_mapping, graph_color=".3 .5 .7", color='darkblue', cross=False):
    experiment = "experiment-2" if not cross else "experiment-2-crosstalk"
    path = pathlib.Path("{}/vis/{}".format(dist_uri, experiment))
    path.mkdir(parents=True, exist_ok=True)
    output = path.absolute().as_posix()
    
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
                vp.set_linewidth(0.5)
                vp.set_alpha(0.5) 
                k = k + 1     
            for partname in ('cbars','cmins','cmaxes','cmedians'): # cmeans
                vp = parts[partname]
                vp.set_edgecolor('black')
                vp.set_linewidth(1)  
                vp.set_alpha(0.7)        
                        
            
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
    plt.savefig("{}/vis-2{}.png".format(output, "-crosstalk" if cross else ""), dpi=dpi)
    print("{}/vis-2{}.png".format(output, "-crosstalk" if cross else ""))
    plt.close(fig)

    # Now make a relative distance plot
    param_sets = range(0, 12) # len(experiment_data[2]["parameters"])
    for param_set in param_sets:
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

        # plt.clf()
        dt = [('len', float)]
        param_data = experiment_data[2]["parameters"][param_set]
        size = "small" if param_data["size"] == 100 else "large"

        # Do some fixing
        prefer_ltr = True
        new_distances = distances[:]
        edges = []
        for i in range(0,5):
            for j in range(0,5):
                if i >= j:
                    new_distances[i][j] = distances[i][j] if prefer_ltr else distances[j][i]
                    new_distances[j][i] = distances[i][j] if prefer_ltr else distances[j][i]
                    if i != j:
                        edges.append("vm{} -- vm{} [len={}, color=\"{} .6\", style=filled, penwidth=3];".format(i, j, 3*new_distances[i][j], graph_color))

        dot_file_contents = r'graph G { node [shape=circle, style=filled, color="' + graph_color + r'", width=0.1, height=0.1, fontcolor=white, fontname="Libertine", fontsize=17]; ' + " ".join(edges) + r' }'
        output_file_path = "{}/vis-1-{}-{}{}".format(output, size, param_data["interval"], "-crosstalk" if cross else "")
        os.system("touch {}.dot".format(output_file_path))
        f = open("{}.dot".format(output_file_path), "w")
        f.write(dot_file_contents)
        f.close()
        os.system("neato -Tsvg -o{}.svg {}.dot".format(output_file_path, output_file_path))
        os.system("rm {}.dot".format(output_file_path))
        print("{}.svg".format(output_file_path))

        # average = np.median([np.mean([i for i in x if i != 0]) for x in new_distances])
        # A = np.power(np.array([tuple(x) for x in new_distances]) / average, 3)
        # A = np.array([tuple(x) for x in new_distances])
        # print(A)

        # G = nx.drawing.nx_agraph.read_dot("{}.dot".format(output_file_path))
        # ("{}.dot".format(output_file_path))
        # G = nx.relabel_nodes(
        #     G, dict(zip(range(len(G.nodes())), keys))
        # )    


        # G = nx.drawing.nx_agraph.to_agraph(G)
        # pos = nx.spring_layout(G, iterations=2000)
        # plt.figure(figsize=(8,8), tight_layout=False) 
        # nx.draw(G, pos, with_labels=True, font_color='white', node_size=8000, font_size=40, font_family='Palatino', width=4, edge_color=color, node_color=color, font_weight='bold')
        # plt.margins(0.2)
        # plt.savefig("{}/vis-1-{}-{}{}.png".format(output, param_data["interval"], size, "-crosstalk" if cross else ""), dpi=dpi, pad_inches=3.5)
        # plt.close()
        # G.draw('/tmp/out.dot', format='dot', prog='neato')
