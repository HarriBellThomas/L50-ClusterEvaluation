#!/usr/bin/env python3
import argparse
import os
import time
from IPy import IP
from remote_setup import run_remote_setup, reset_remote
from importlib import import_module
import getpass
import yaml

#
def run_experiment(exp_num, target, pswd, definition):
    if check_experiment_number(exp_num):
        argument_sets = definitions['parameters'] if 'parameters' in definition else [[]]
        for i in range(len(argument_sets)): 
            args = argument_sets[i]
            print("-- Experiment {}.{} --".format(exp_num, i))
            print("Description: {}".format(definition['name'] if 'name' in definition else '(none)'))
            print("Argument set: {}".format(args))

            run_remote_setup(exp_num, target, pswd)
            sleep(2)
            directory = os.path.dirname(os.path.abspath(__file__))
            os.system("python3 {}/{}/run.py {}".format(directory, exp_num, target))
            time.sleep(2)
            reset_remote(target, pswd)
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
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an experiment.')
    parser.add_argument('-e','--experiment', help='Which experiment to run. Omit to run all.', default=0)
    parser.add_argument('-t','--target', help='Target IP address.', required=True)
    args = parser.parse_args()
    
    try:
        directory = os.path.dirname(os.path.abspath(__file__))
        experiment_data = {}
        with open("{}/definitions.yml".format(directory), 'r') as stream:
            data = yaml.safe_load(stream)
            if 'experiments' in data:
                for item in data['experiments']:
                    if 'id' in item:
                        experiment_data[item['id']] = item
        print(experiment_data)

        ip = IP(args.target)
        pswd = getpass.getpass('SSH password for L50: ')

        experiment_name = "all experiments" if args.experiment == 0 else "experiment {}".format(args.experiment)
        print("\nRunning {} against {}...".format(experiment_name, ip))
        print("--------------------------------\n")

        if args.experiment == 0:
            for experiment in get_all_experiments():
                exp_definition = experiment_data[experiment] if experiment in experiment_data else {}
                run_experiment(experiment, args.target, pswd, exp_definition)
                print("--------------------------------\n")
                time.sleep(0.5) # Increase
        else:
            exp_definition = experiment_data[args.experiment] if args.experiment in experiment_data else {}
            run_experiment(args.experiment, ip, pswd, exp_definition)
    except ValueError:
        print("Invalid IP address: {}".format(args.target))