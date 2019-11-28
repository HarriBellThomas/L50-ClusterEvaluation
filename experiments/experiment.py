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
import smtplib
from email.message import EmailMessage


#
def run_experiment(targets, definition):
    experiment_source = definition.get("src", definition.get("id", -1))
    if validate_experiment(experiment_source):
        # Init experiment.
        exp_num = definition.get("id", -1)
        print("---[BEGIN EXPERIMENT]---\n")
        _id = str(uuid.uuid4())  # Unique ID to track experiment. 
        results_dir = prepare_for_experiment(_id, ", ".join(targets), definition)

        # Iterate over arguments variations.
        argument_sets = definition.get('parameters', [[]])
        for i in range(len(argument_sets)): 
            args = argument_sets[i].copy()
            args["_id"] = _id
            args["_run"] = i
            args["_desc"] = definition.get('description', '(none)')
            serialised_args = json.dumps(args)

            # Coordinate and execute according to target policy.
            # targets_config = definition.get("targets")
            for t in range(len(targets)):
                target = targets[t]
                prepare_for_target(_id, i, target, definition, argument_sets[i])
                print("-- Experiment {}.{}.{} --".format(exp_num, t, i))
                print("Target: {}".format(target))
                print("Description: {}".format(definition.get('description', '(none)')))
                print("Argument set: {}".format(args))

                run_remote_setup(experiment_source, target, serialised_args, _id)
                directory = os.path.dirname(os.path.abspath(__file__))
                os.system("python3 {}/{}/run.py {} '{}' {}".format(
                    directory, experiment_source, target, serialised_args, results_dir
                ))
                time.sleep(2)
                reset_remote(experiment_source, target, _id, i, results_dir)
                print("")

        print("---[END EXPERIMENT]---\n")
        print("\nID: {}\n".format(_id))
    else:
        print("Invalid experiment source.")


#
def validate_experiment(source):
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.exists("{}/{}/run.py".format(directory, source))

#
def get_all_experiments():
    valid = True
    current = 0
    while(valid):
        current = current + 1
        valid = check_experiment_number(current)
    return range(1, current)

#
def prepare_for_experiment(_id, targets, meta):
    _desc = meta.get("description", "(none)")
    _paramSets = meta.get("parameters", [{}])
    _runs = len(_paramSets)
    _time = time.ctime()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(_runs):
        path = pathlib.Path("{}/results/data/{}/{}".format(script_dir, _id, i))
        path.mkdir(parents=True, exist_ok=True)
        results_dir = path.absolute().as_posix()

        # Write per-run explainer.
        f = open("{}/results/data/{}/{}/explain".format(script_dir, _id, i), "w+")
        f.write("{} -> {}\nDescription: {}\nTime: {}\nArgs: {}".format(
            str(socket.gethostbyname(socket.gethostname())),
            str(targets), _desc, _time, json.dumps(_paramSets[i])
        ))
        f.close()

    # Write top level explainer.
    f = open("{}/results/data/{}/overview".format(script_dir, _id), "w+")
    f.write("{} -> {}\nDescription: {}\nTime: {}\nRuns:\n".format(
        str(socket.gethostbyname(socket.gethostname())), 
        str(targets), _desc, _time
    ))
    for i in range(_runs):
        f.write("   {}: {}\n".format(i, json.dumps(_paramSets[i])))
    f.close()

    # Append to experiment log.
    f = open("{}/results/contents".format(script_dir), "a+")
    f.write("{}  {}  {}\n".format(
        meta.get('name', '(none)'), _time, _id
    ))
    f.close()

    return pathlib.Path("{}/results/data/{}".format(script_dir, _id)).absolute().as_posix()

#
def prepare_for_target(_id, run, target, meta, parameters):
    _desc = meta.get("description", "(none)")
    _time = time.ctime()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    path = pathlib.Path("{}/results/data/{}/{}/{}".format(script_dir, _id, run, target))
    path.mkdir(parents=True, exist_ok=True)
    results_dir = path.absolute().as_posix()

    # Write explainer for target in experiment run.
    f = open("{}/explain".format(results_dir), "a+")
    f.write("{} -> {}\nDescription: {}\nTime: {}\nArgs: {}".format(
        str(socket.gethostbyname(socket.gethostname())), str(target), 
        _desc, _time, parameters
    ))
    f.close()

#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an experiment.')
    parser.add_argument('-e','--experiment', help='Which experiment to run. Omit to run all.', default=0)
    parser.add_argument('-t','--target', help='Target IP address.', required=True)
    parser.add_argument('-l','--lmk', help='Email to notify when done.', default=False)
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

    # Parse and verify targets.
    targets = [t.strip() for t in args.target.split(",")] if "," in args.target else [args.target]
    for target in targets:
        try:
            ip = IP(target)
        except ValueError:
            print("Invalid IP address: {}".format(target))

    experiment_name = "all experiments" if args.experiment == 0 else "experiment {}".format(args.experiment)
    print("\nRunning {}...\n".format(experiment_name))

    if args.experiment == 0:
        for experiment in get_all_experiments():
            exp_definition = experiment_data.get(experiment, {})
            run_experiment(targets, exp_definition)
            time.sleep(0.5) # Increase
    else:
        exp_definition = experiment_data.get(int(args.experiment), {})
        run_experiment(targets, exp_definition)
    

    if args.lmk:
        msg = EmailMessage()
        msg.set_content("Test message")
        msg['Subject'] = 'Test'
        msg['From'] = "server@L50.cl.cam.ac.uk"
        msg['To'] = args.lmk
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
