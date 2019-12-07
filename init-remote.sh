#!/bin/sh
! test -f ~/.ssh/evaluation && echo "No key installed. Run init.sh." && return;
cat ~/.ssh/evaluation.pub | ssh L50@$1 'cat >> ~/.ssh/authorized_keys && echo "Key copied"'
scp -o StrictHostKeyChecking=no -i ~/.ssh/evaluation ~/.ssh/evaluation.pub L50@$1:~/.ssh/evaluation.pub
scp -o StrictHostKeyChecking=no -i ~/.ssh/evaluation ~/.ssh/evaluation L50@$1:~/.ssh/evaluation
ssh -t -o StrictHostKeyChecking=no -i ~/.ssh/evaluation L50@$1 '[ ! -d "x" ] && git clone https://github.com/HarriBellThomas/L50-ClusterEvaluation.git x; cd x; git pull; ./init.sh'