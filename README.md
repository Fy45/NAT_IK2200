


# NAT - Development of a multi-threaded NAT

In order to give a clearer view, I delete all the test configuration and only leave the working scripts. Also, if you want to see the development process you can go to the ReadME file for each task. The script outside all the folders is the one under development.

Here is the README for [Task 1](https://github.com/Fy45/NAT_IK2200/blob/master/Code/task1/README.md)

README for [Task 2](https://github.com/Fy45/NAT_IK2200/blob/master/Code/task2/README.md)

## Task 1 - Develop a single core NAT

The configuration of single-core NAT is based on Click language and is run with FastClick. In order to fulfil the NAT, we need to realize functions by using Click Elements. The following Figure is a flowchart to show how the configuration finishes the NAT process.

![Flowchart of Single-core NAT configuration](https://github.com/Fy45/NAT_IK2200/blob/master/Code/task1/Single-core%20NAT.jpg)

First, when the NAT machine received a packet, it needs to distinguish the type of the packet. If the packet is an ARP request, NAT will generate the response and send it to the corresponding interface. If the packet is an ARP response, then NAT will encapsulate ethernet header found via ARP into IP packets. If the packet is an IP packet, NAT will classify its type (TCP, UDP or ICMP) and send the packet into corresponding Rewriter Elements.

It is really similar for TCPRewriter, UDPRewriter, ICMPRewriter, and ICMPPingRewriter elements. The parameter that they use, is from IPRewriterPatterns, which specify the new source IP address and source port. After all of these finished, NAT will broadcast the ARP query to request the Ethernet address of destination machine and send out the rewritten packet.

## Task 2 - Develop a multi-thread NAT

### Per-core duplication, with software classification

Really similar to the previous task, but what we need to add is to using CPUSwitch element in order to duplicate the process of NAT function. When a packet comes back, we need to send it to a corresponding Rewrite flow table based on its destination port.

You can see the whole configuration in 2-core-NAT.click and 4-core-NAT.click. I will update the explanation for the script.

To be continued....

>>>>>>>
