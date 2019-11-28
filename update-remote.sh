#!/bin/sh
ssh -i ~/.ssh/evaluation L50@$1 '[ ! -d "x" ] && git clone https://github.com/HarriBellThomas/L50-ClusterEvaluation.git x; cd x; git pull;'