#!/usr/bin/env python3
import argparse
import os
import time
from IPy import IP
from remote_setup import run_remote_setup
from importlib import import_module
import getpass

#
def run_experiment(exp_num, target, pswd):
    if check_experiment_number(exp_num):
        print("-- Experiment {} --".format(exp_num))
        run_remote_setup(exp_num)

        os.system("python3 {}/run.py {}".format(exp_num, pswd))
    else:
        print("Invalid experiment number")

#
def check_experiment_number(exp_num):
    return os.path.exists("{}/run.py".format(exp_num))

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
        ip = IP(args.target)
        pswd = getpass.getpass('SSH password for L50: ')

        experiment_name = "all experiments" if args.experiment == 0 else "experiment {}".format(args.experiment)
        print("\nRunning {} against {}...".format(experiment_name, ip))
        print("--------------------------------\n")

        if args.experiment == 0:
            for experiment in get_all_experiments():
                run_experiment(experiment, args.target, pswd)
                print("--------------------------------\n")
                time.sleep(0.5) # Increase
        else:
            run_experiment(args.experiment, ip, pswd)
    except ValueError:
        print("Invalid IP address: {}".format(args.target))