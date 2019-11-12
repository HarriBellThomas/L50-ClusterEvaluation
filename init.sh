#!/bin/sh
if [ ! $INITIALISED ] ; then
    # Run setup phase as root.
    sudo apt-get update -y
    sudo apt-get install iperf iperf3 traceroute python3-pip -y

    pip3 install --upgrade pip
    pip install IPy paramiko pyyaml --user

    # Get the eth0 IP address.
    export HOST="$(hostname)"
    export IP_ADDR="$(hostname --ip-address)"
    echo "$HOST: $IP_ADDR"

    export INITIALISED=true
fi