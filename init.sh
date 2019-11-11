#!/bin/sh
if [ ! $INITIALISED ] ; then
    # Run setup phase as root.
    sudo apt-get update
    sudo apt-get install iperf iperf3 traceroute -y
    exit

    pip3 install IPy paramiko

    # Get the eth0 IP address.
    export HOST="$(hostname)"
    export IP_ADDR="$(hostname --ip-address)"
    echo "$HOST: $IP_ADDR"

    export INITIALISED=true
fi