# L50: Azure Cluster Characterisation

This framework is split into 3 modules; experiments, distribute, and analysis.

experiments --- this module contains the definition of all the experiment the framework can, as well as their source code and the control logic that actually runs them. The main file is experiment.py, and its usage is given in the report.

distribute --- the framework is designed to run fully autonomously, sequentially running each experiment from every host acting as the master. These scripts facilitate this, including the repatriation of all data collected to the origin node. The main file is distribute.py.

analysis --- finally, this module is designed to take output from the distribution module and generate all the graphs used in this report from the source recordings. The main file is analyse.py

---

For reference, the IP-VM name mappings are as follows.

Cluster 1:
vm0 -> 10.0.0.4
vm1 -> 10.0.0.6
vm2 -> 10.0.0.7
vm3 -> 10.0.0.8
vm4 -> 10.0.0.5

Cluster 2:
vm0 -> 10.0.0.6
vm1 -> 10.0.0.5
vm2 -> 10.0.0.4
vm3 -> 10.0.0.8
vm4 -> 10.0.0.7

