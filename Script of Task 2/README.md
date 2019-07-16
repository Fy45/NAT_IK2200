## 18-10-14

Until now I have finished the NAT for multi-core support based on software classification method. There are three files during the development which also represent three stages of the development. 

First is to write a simple forwarding configuration with multi-core supported. This requires to duplicate and handle the session for ARP query and response.

Second is to duplicate the NAT function based on the previous stage. The problem is to send the packets to the correct Rewrite element based on their destination port. Otherwise, generate will never receive any ACK from Sink machine since all the return packets will be dropped by the NAT.

Third is to extend the 2-core script to 4-core. You can see all the script in this folder

\-Hongyi

## 18-10-18

Another method to implement the multi-core NAT is using *Spinlock* around the flow table, protecting the share states between cores. Our code script is applying the spinlock elements based on single-core NAT script.

The very first step is to add HTTPServer element from FastClick to enable using our navigator to browse the elements and the handlers for testing in the future steps. 

At this stage, we temporarily apply the lock around the *IPRewriter* to realize the function. Testing the script has the main issue with transmitting rate, we are working on solving this. The next stage we are aiming at modifying the Rewriter element itself to realize the fine-grained lock.

\-Yuan&Xuwei&Huanyu

## 18-10-19
We have finished two types of *Spinlock*. The first is to lock TCPRewriter and UDPRewriter elements, the second is to lock the operationa about flowtable inside TCPRewriter and UDPRewriter elements. The stuctures of both spinlock types are shown in .jpg files. The detailed code can be seen in this fold too.

Our next step is to evalue their performance and compare it with single-core NAT.

\-Xuwei

