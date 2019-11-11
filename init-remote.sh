#!/bin/sh
ssh L50@$1 -c '[ ! -d "L50-ClusterEvaluation" ] && git clone https://github.com/HarriBellThomas/L50-ClusterEvaluation.git; cd L50-ClusterEvaluation; git pull; ./init.sh'