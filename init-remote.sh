#!/bin/sh
! test -f ~/.ssh/evaluation && echo "No key installed. Run init.sh." && return;
cat ~/.ssh/evaluation.pub | ssh L50@$1 'cat >> .ssh/authorized_keys && echo "Key copied"'
ssh -i ~/.ssh/evaluation L50@$1 '[ ! -d "L50-ClusterEvaluation" ] && git clone https://github.com/HarriBellThomas/L50-ClusterEvaluation.git; cd L50-ClusterEvaluation; git pull; ./init.sh'