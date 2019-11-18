# Test Plan

1. Check whether the host is reachable using `ping`.
2. traceroute to determine if hosts are directly connect or not. (If not a sipmole fully connected graph, are packets always routed the same way?)
3. Use the ping tool to assess the latency between the two machines. This will involve experimenting with all the main flag options (such as packer size, window size, buffer length) to exhibit any inherent behaviour of the NIC.
4. Bandwidth tests with iperf(3). Again iterating over the potential option flags to ensure any parent NIC behaviour is exposed. Want to determine if different traffic classes are treated differently (ICMP, TCP, UDP).
5. Repeat 4 with different rx-usecs values.
6. Try to determine what the Ethernet standard being used is -- eg are we seeing 64b/66b line coding? Probably via manual inspection.
