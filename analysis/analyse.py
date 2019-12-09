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

from experiment_1 import plot_iperf_results
from experiment_2 import plot_ping_topology, aggregate_ping_topology_data
from experiment_4 import experiment_4
from experiment_5 import experiment_5, experiment_5_aggregated
from experiment_6 import experiment_6, experiment_6_aggregated

# plt.rcParams['figure.dpi'] = 600 
plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{libertine}\usepackage[libertine]{newtxmath}\usepackage{sfmath}\usepackage[T1]{fontenc}'
# plt.rcParams['figure.figsize'] = 8, 4

colourmap = {"vm0": "green", "vm1":"red", "vm2":"orange", "vm3":"darkblue", "vm4":"purple"}
dpi = 600
cluster1_mapping = {"10.0.0.4":"vm0", "10.0.0.6":"vm1", "10.0.0.7":"vm2", "10.0.0.8":"vm3", "10.0.0.5":"vm4"}
cluster2_mapping = {"10.0.0.6":"vm0", "10.0.0.5":"vm1", "10.0.0.4":"vm2", "10.0.0.8":"vm3", "10.0.0.7":"vm4"}
cluster1_node_color = '.133, .545, .133'
cluster1_edge_color = '.133, .545, .133'
cluster2_node_color = '.133, .545, .133'
cluster3_edge_color = '.133, .545, .133'

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


def process_directory(path, experiment_data):
    dist_path = pathlib.Path(path)
    dist_uri = dist_path.absolute().as_posix()

    if dist_path.exists():
        # visualise_experiments(experiment_data, dist_uri)
        if int(args.cluster) == 1:
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, '#0080ff', 'darkblue')
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, '#0080ff', 'darkblue', cross=True)
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping)
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping, cross=True)
            experiment_4(experiment_data, dist_uri, cluster1_mapping)
            experiment_4(experiment_data, dist_uri, cluster1_mapping, cross=True)
            experiment_5(experiment_data, dist_uri, cluster1_mapping)
            experiment_6(experiment_data, dist_uri, cluster1_mapping)
        elif int(args.cluster) == 2:
            plot_ping_topology(experiment_data, dist_uri, cluster2_mapping, '#FC3236', 'darkred')
            plot_ping_topology(experiment_data, dist_uri, cluster2_mapping, '#FC3236', 'darkred', cross=True)
            plot_iperf_results(experiment_data, dist_uri, cluster2_mapping)
            plot_iperf_results(experiment_data, dist_uri, cluster2_mapping, cross=True)
            experiment_4(experiment_data, dist_uri, cluster2_mapping)
            experiment_4(experiment_data, dist_uri, cluster2_mapping, cross=True)
            experiment_5(experiment_data, dist_uri, cluster2_mapping)
            experiment_6(experiment_data, dist_uri, cluster2_mapping)
        else:
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, 'orange')
            plot_ping_topology(experiment_data, dist_uri, cluster1_mapping, 'orange', cross=True)
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping)
            plot_iperf_results(experiment_data, dist_uri, cluster1_mapping, cross=True)
            experiment_4(experiment_data, dist_uri, cluster1_mapping)
            experiment_4(experiment_data, dist_uri, cluster1_mapping, cross=True)
            experiment_5(experiment_data, dist_uri, cluster1_mapping)
            experiment_6(experiment_data, dist_uri, cluster1_mapping)

    else: 
        print("Path doesn't exist.")

######################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse experiments.')
    parser.add_argument('-p','--path', nargs='+', help='Which distribution to analyse.', required=True)
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

    paths = args.path
    if len(paths) > 1:
        print("Generating graphs across multiple runs...")
        p = pathlib.Path("{}/aggregations/cluster{}".format(dirname(os.path.abspath(__file__)), args.cluster))
        p.mkdir(parents=True, exist_ok=True)
        output_path = p.absolute().as_posix()
        for dir in ["experiment2", "experiment2-crosstalk", "experiment5", "experiment6"]:
            pathlib.Path("{}/{}".format(output_path, dir)).mkdir(parents=True, exist_ok=True)
        print("Output path: {}".format(output_path))

        # Plot combined graphs.
        dist_uris = []
        for path in paths:
            dist_path = pathlib.Path(path)
            if dist_path.exists():
                dist_uris.append(dist_path.absolute().as_posix())
            else:
                print("Rejected: {}".format(path))

        if args.cluster == 1:
            aggregate_ping_topology_data(output_path + "/experiment2", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping, '#0080ff', 'darkblue', cross=False)
            aggregate_ping_topology_data(output_path + "/experiment2-crosstalk", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping, '#0080ff', 'darkblue', cross=True)
        else:
            aggregate_ping_topology_data(output_path + "/experiment2", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping, '#FC3236', 'darkred', cross=False)
            aggregate_ping_topology_data(output_path + "/experiment2-crosstalk", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping, '#FC3236', 'darkred', cross=True)

        experiment_5_aggregated(output_path + "/experiment5", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping)
        experiment_6_aggregated(output_path + "/experiment6", experiment_data, dist_uris, cluster1_mapping if args.cluster == 1 else cluster2_mapping)

    else:
        # Plot all graphs for a single run.
        process_directory(str(paths[0]), experiment_data)


