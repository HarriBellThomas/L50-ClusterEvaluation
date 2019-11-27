#!/usr/bin/env python3
import argparse
import os
import time
from IPy import IP
from remote_setup import run_remote_setup, reset_remote
from importlib import import_module
import getpass
import yaml
import json
import uuid
import pathlib
import socket

#
def run_experiment(exp_num, target, definition):
    if check_experiment_number(exp_num):
        argument_sets = definition.get('parameters', [[]])
        print("---[BEGIN EXPERIMENT]---\n")
        for i in range(len(argument_sets)): 
            args = argument_sets[i]
            print("-- Experiment {}.{} --".format(exp_num, i))
            print("Description: {}".format(definition.get('description', '(none)')))
            print("Argument set: {}".format(args))

            # Unique ID to track experiment. 
            _id = str(uuid.uuid4())
            args["_id"] = _id
            args["_run"] = i
            args["_desc"] = definition.get('description', '(none)')
            serialised_args = json.dumps(args)

            run_remote_setup(exp_num, target, serialised_args)
            directory = os.path.dirname(os.path.abspath(__file__))
            os.system("python3 {}/{}/run.py {} '{}'".format(
                directory, exp_num, target, serialised_args
            ))
            time.sleep(2)
            reset_remote(exp_num, target)
            print("")
        print("---[END EXPERIMENT]---\n")
    else:
        print("Invalid experiment number")

#
def check_experiment_number(exp_num):
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.exists("{}/{}/run.py".format(directory, exp_num))

#
def get_all_experiments():
    valid = True
    current = 0
    while(valid):
        current = current + 1
        valid = check_experiment_number(current)
    return range(1, current)

#
def prepare_for_experiment(args, serialised, target):
    _id = args.get("_id")
    _run = args.get("_run")
    _desc = args.get("_desc")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = pathlib.Path("{}/results/{}/{}".format(script_dir, _id, _run))
    path.mkdir(parents=True, exist_ok=True)
    results_dir = path.absolute().as_posix()

    f = open("{}/explain".format(results_dir), "w")
    f.write("{} -> {}\nDescription: {}\nTime: {}\nArgs: {}".format(
        str(socket.gethostbyname(socket.gethostname())), str(target), 
        _desc, time.ctime(), serialised
    ))
    f.close()

    return path.absolute().as_posix()

#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an experiment.')
    parser.add_argument('-e','--experiment', help='Which experiment to run. Omit to run all.', default=0)
    parser.add_argument('-t','--target', help='Target IP address.', required=True)
    args = parser.parse_args()
    # pswd = getpass.getpass('SSH password for L50: ')

    directory = os.path.dirname(os.path.abspath(__file__))
    experiment_data = {}
    with open("{}/definitions.yml".format(directory), 'r') as stream:
        data = yaml.safe_load(stream)
        if 'experiments' in data:
            for item in data['experiments']:
                if 'id' in item:
                    experiment_data[item['id']] = item

    targets = [t.strip() for t in args.target.split(",")] if "," in args.target else [args.target]
    for target in targets:
        try:
            ip = IP(target)

            experiment_name = "all experiments" if args.experiment == 0 else "experiment {}".format(args.experiment)
            print("\nRunning {} against {}...\n".format(experiment_name, ip))

            if args.experiment == 0:
                for experiment in get_all_experiments():
                    exp_definition = experiment_data.get(experiment, {})
                    run_experiment(experiment, target, exp_definition)
                    time.sleep(0.5) # Increase
            else:
                exp_definition = experiment_data.get(int(args.experiment), {})
                run_experiment(args.experiment, ip, exp_definition)
        except ValueError:
            print("Invalid IP address: {}".format(target))