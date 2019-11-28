#!/bin/bash
if [ ! $INITIALISED ] ; then
    # Run setup phase as root.
    sudo apt-get update -y
    sudo apt-get install iperf iperf3 traceroute python3-pip -y

    sudo -H pip3 install --upgrade pip
    sudo -H pip3 install IPy paramiko pyyaml scp

    # Generate SSH key if it doesn't exist.
    ! test -f ~/.ssh/evaluation && ssh-keygen -t rsa -N "" -f ~/.ssh/evaluation
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/evaluation
    touch ~/.ssh/config && echo "IdentityFile ~/.ssh/evaluation" > ~/.ssh/config

    # Clean up the terminal to make it nicer to work with.
    touch ~/.hushlogin
    echo 'startup_message off' > ~/.screenrc
    echo 'function g() { ssh -o StrictHostKeyChecking=no L50@"10.0.0.$1"; }' > ~/.bash_profile
    echo 'export PS1="\e[1;92m\h  \w  \e[21;97m"' >> ~/.bash_profile
    echo 'alias u="cd ~/x; git pull"' >> ~/.bash_profile
    echo 'function e() { cd ~/x/experiments; python3 experiment.py -e $1 -t "10.0.0.$2"; }' > ~/.bash_profile
    source ~/.bash_profile

    # Get the eth0 IP address.
    export HOST="$(hostname)"
    export IP_ADDR="$(hostname --ip-address)"
    echo "$HOST: $IP_ADDR"

    export INITIALISED=true
fi