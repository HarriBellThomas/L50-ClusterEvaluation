# Test Plan
0. Metadata for the machines, simple but important. Basic experiments are just creating a picture of what the machines are able to do. Check against the Azure documentation.
1. Check whether the host is reachable using `ping`.
2. traceroute to determine if hosts are directly connect or not. (If not a sipmole fully connected graph, are packets always routed the same way?)
3. Use the ping tool to assess the latency between the ~~two~~ all machines (concurrent experiments, shared medium etc). This will involve experimenting with all the main flag options (such as packer size, window size, buffer length) to exhibit any inherent behaviour of the NIC. Need to justify the choices made for the experiments.
4. Bandwidth tests with iperf(3). Again iterating over the potential option flags to ensure any parent NIC behaviour is exposed. Want to determine if different traffic classes are treated differently (ICMP, TCP, UDP). Verify that ICMP is limited to 100 Mbps, as its supposed to be.
5. Repeat 4 with different rx-usecs values.
6. ~~Try to determine what the Ethernet standard being used is -- eg are we seeing 64b/66b line coding? Probably via manual inspection. (Not possible probably.)~~
7. Accurate traffic profiling. MoonGen may be able to be used, otherwise tcprelay or other tools if found. Want to see if any artefact of the Azure VLAN can be detected -- eg NIC/switch cadences.


How does Azure VPN configuration affect throughput?
Need to check the accuracy of timings between the two machines.

Different the ports? Profile over time? Streaming vs torrenting? User-perspective characterisation.
