#!/usr/bin/env python3
import sys
import os
from os.path import dirname, abspath
sys.path.insert(1, "{}/analysis/helpers".format(dirname(dirname(dirname(abspath(__file__))))))
import glob
from parse import parse_iperf_local
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import uuid

mpl.rcParams['figure.dpi'] = 600 
mpl.rc('text', usetex = True) 
mpl.rcParams['font.size'] = 12 
# mpl.rcParams['text.latex.preamble'] = r"\usepackage{libertine},\usepackage[libertine]{newtxmath},\usepackage[T1]{fontenc}"
mpl.rcParams['figure.figsize'] = 5, 4


def draw(xs, ys, out):
    plt.clf()
    plt.plot(xs, ys)
    plt.savefig(out)
    plt.clf()


if __name__ == "__main__":
    input = sys.argv[1]
    output = sys.argv[2]

    # temp hack
    _parts = input.split("/")
    _uuid = _parts[len(_parts) - 1]

    parameter_sets = glob.glob("{}/{}/*".format(input, _uuid))
    for param_set in parameter_sets:
        targets = glob.glob("{}/*".format(param_set))
        for t in targets:
            if os.path.isdir(t):
                increment = 0.5
                values = parse_iperf_local("{}/local".format(t), 4)
                if len(values) > 2:
                    times = np.arange(0, len(values)*0.5, 0.5).tolist()
                    draw(times, values, "{}/{}.png".format(output, str(uuid.uuid4())))
                    print("ping -> {}: {}".format(t.split("/")[-1], parse_iperf_local("{}/local".format(t))))
        


    # print("{} -> {}".format(input, output))
    # parse_iperf_local("{}/local".format(input))