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


def visualise_experiments(definitions, data_path):
    parent_directory = dirname(dirname(os.path.abspath(__file__)))
    for key in definitions:
        paths_to_parse = glob.glob("{}/**/*-experiment-{}".format(data_path, key))
        for path in paths_to_parse:
            path_parts = path.split("/")
            output_path = pathlib.Path("{}/experiment-{}/{}".format(data_path, key, path_parts[len(path_parts)-2]))
            output_path.mkdir(parents=True, exist_ok=True)
            # print("call {} on {} outputting to {}".format(
            #     "{}/experiments/{}/visualise.py".format(),
            #     path,
            #     output_path.absolute().as_posix()
            # ))
            visualisation_script = pathlib.Path("{}/experiments/{}/visualise.py".format(parent_directory, definitions[key]["src"]))
            if visualisation_script.exists():
                os.system("python3 {} {} {}".format(
                    visualisation_script.absolute().as_posix(),
                    path,
                    output_path.absolute().as_posix()
                ))
            else:
                print("Can't find visualisation script")

    # script_dir_parent = dirname(dirname(os.path.abspath(__file__)))
    # path = pathlib.Path("{}/experiments".format(script_dir_parent, args.distribution))


#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse experiments.')
    parser.add_argument('-p','--path', help='Which distribution to analyse.', required=True)
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

    if dist_path.exists():
        visualise_experiments(experiment_data, dist_uri)
    else: 
        print("Path doesn't exist.")
