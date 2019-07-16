# NAT - Development of a multi-threaded NAT

Network Address Translation (NAT) is a technology which is widely deployed today. It aims to address the problem of the insufficient number of public IPv4 addresses. With the increasing expansion of today’s networks, simply using traditional NAT can no longer fulfill Internet Service Provider’s (ISP) requirements of deploying a large scale of network. This leads to the concept of Carrier Grade NAT (CGN). The main purpose of this project is to study different methods on how to build a CGN on a single host with multiple CPU cores. Starting with a single-core NAT realization, the project focuses on building a multi-threaded NAT in various ways to improve the performance of a single-core NAT.

## Task 1 - Develop a single core NAT

The configuration of single-core NAT is based on Click language and is run with FastClick. In order to fulfil the NAT, we need to realize functions by using Click Elements. The following Figure is a flowchart to show how the configuration finishes the NAT process.

![Flowchart of Single-core NAT configuration](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/single-coreNAT.png)

First, when a NAT machine receives a packet, it needs to distinguish the type of the packet. If the packet is an ARP request, NAT will generate a response and send it to the corresponding interface. If the packet is an ARP response, then NAT will encapsulate ethernet header, which is found via ARP, into IP packets. If the packet is an IP packet, NAT will classify its type (TCP, UDP or ICMP) and send the packet into corresponding Rewriter Elements.
The procedures for the different rewriter elements are really similar. The elements used in single-core NAT are TCPRewriter, UDPRewriter, ICMPRewriter, and ICMPPingRewriter elements. The parameters which specify the new source IP addresses and source ports in these Rewriter Elements is from IPRewriterPatterns. After all of these finished, NAT will broadcast a ARP query to request the Ethernet address of destination machine and send out the rewritten packet.

## Task 2 - Develop a multi-thread NAT

### Global Locked Flow Table

This solution is to use lock to block threads to prevent muti-thread handle NAT's flow table at same time. We have three ways to add lock to muti-thread NAT. The first one is the most simple one, we use Spinlock elements to lock the elements that relative to NAT flow table. In our case, TCPRewriter and UDORewriter are been locked by *SpinlockAcquire* and *SpinlockRelease* elements. The stucture is shown below:

![SpinLock by using FastClick Elements](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/lockelement.png)

However, blocking whole elements will waste time ,for some operations irrelative to flowtable are been blocked as well. If we only simply use lockaquire and release elements, this rough lock will lock up all the rewriting operation. This also includes some unnecessary functions, which will greatly slow down the acquisition of locks by other CPUs. In order to avoid this defect, we introduced a finer-grained lock. The following figure is roughly based on file udprewriter.cc and shows how a UDP packet goes through the UDP Rewriter element.

![Packet handling process of UDPRewriter](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/Finer-grained.png)

Also, you can find the locked FastClick version in branch [FastClick_Locked](https://gits-15.sys.kth.se/yfan/IK2200_NAT/tree/FastClick_Locked).

### Per-core duplication, with software classification

Really similar to the previous task, but what we need to add is to using CPUSwitch element in order to duplicate the process of NAT function. When a packet comes back, we need to send it to a corresponding Rewrite flow table based on its destination port. The following figure shows a flow chart while using Multi-core NAT.

![Flow chart of Multi-core NAT](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/multisoft.png)

For each Rewriter Element, they maintain different flow tables. For example, TCP and UDP Rewriter under CPU 0 maintain flow table 0. After choosing the corresponding CPU, the packets will be rewritten and sent to the corresponding ToDPDKDevice Element. And while dealing with return ACK packets, the following flowchart shows how a NAT will work.

![Flow chart of Return ACK](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/acksoft.png)

When an ACK comes back from the destination terminal, NAT will classify the destination port and push the packet to the corresponding flow table. For example, packets pushed to CPU 0 will be rewritten the source port within range 5000-5500, then the returning ACKs within destination port range 5000-5500 will be pushed to flow table 0, which maintain the mapping to the original packet.

### Per-core duplication, with hardware classification

The idea of hardware classification is identical to the software classification. The only difference is how to deal with those ACKs. In hardware classification, a separate core will be assigned to FromDPDKdevice and IPClassifier elements to complete packets classification and receiving.

![Flow chart of Return ACK in hardware classification](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/ackhard.png)

After achieving the incoming packet, the separate core will check its packet type and destination port, then send it to the corresponding flow table which stores the mapping information of it.

## Task 3 - Literature Review and Improving NAT

### Removing Heap Tree

FastClick uses a heap tree to deal with the time expiry. But, for a multi-threaded NAT, heap tree became a big problem. It is really hard to make multi-threaded safe and only can be maintained by cores separately. In order to deal with this problem, we decided to remove heap tree and introduce a new mechanism to deal with flow timeout. Actually, it can be done directly in the hashtable.
In FastClick, every element stored in the hashtable is added to the head of the link list. After rebalancing, if the link list is over the length threshold, a NAT can delete all the flow elements at the end of the list to ensure the complexity of update and lookup. Also, every flow element queried is changed to the head of the list, so that the active flow will continue to be placed at the front of the list. This will also speed up update and query speed. You may find out the code in branch [FastClick_noheap](https://gits-15.sys.kth.se/yfan/IK2200_NAT/tree/FastClick_noheap).

### Cuckoo Hash

Cuckoo Hashing is a technique for resolving collisions in hash tables that produces a dictionary with constant-time worst-case lookup and deletion operations as well as amortized constant-time insertion operations.

It is multi-thread safe and decreases the lookup operations significantly. The idea is to use two hash functions instead of one, so that there are two buckets for the key to reside in. If all slots in both buckets are full, the key is inserted at a random slot within the two buckets, and the existing key at the randomly chosen slot is evicted and reinserted at another bucket. Figure below shows the process of data packets in Cuckoo Hash.

![Cuckoo Hash](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/FlowChart/cuckoo.png)

Cuckoo hash implementation pushes elements out of their bucket, if there is a new entry to be added which primary location coincides with their current bucket, being pushed to their alternative location. Therefore, as user adds more entries to the hashtable, distribution of the hash values in the buckets will change, being most of them in their primary location and a few in their secondary location, which the later will increase, as table gets busier. This information is quite useful, as performance may be lower as more entries are evicted to their secondary location. You can find out the code at [cuckoohash.hh](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/cuckoohash.hh) and [cuckoohash.cc](https://gits-15.sys.kth.se/yfan/IK2200_NAT/blob/master/cuckoohash.cc)