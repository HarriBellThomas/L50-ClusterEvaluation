# Test Plan

1. Check whether the host is reachable using `ping`.
2. traceroute to determine if hosts are directly connect or not. (If not a sipmole fully connected graph, are packets always routed the same way?)
3. Use the ping tool to assess the latency between the two machines. This will involve experimenting with all the main flag options (such as packer size, window size, buffer length) to exhibit any inherent behaviour of the NIC.
