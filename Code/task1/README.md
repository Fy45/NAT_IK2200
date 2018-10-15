## 18-09-17

This script contains the first try of sending a rewritten IP packet to the certain destination. Also, I want to return the ACK to the corresponding host. This edition will crush: Segmentation fault (core dumped)

Try to be familiar with the Rewriter element and Click the language

I will organize all the scripts into Test/date folders. The outside file will be the latest program which will be continually developed.

\- Hongyi

## 18-09-18

Single-NAT-v2.click solve the core dump problem. We need to avoid using two patterns with the same input, which will cause an empty point problem. But the script still has some of the problems since I didn’t add arp request and reply on Click router. All the information coming to the internal interface is ARP-Requesting. 

I wrote a new program contain all the function. The reference code is mazu-nat.click and thomer-nat.click. But there’s still some problem. It seems that I shouldn’t reuse the ToDevice and FromDevice element with the same interface. I will figure out the solution tomorrow.

\- Hongyi

## 18-09-20

Reused device problem solved. I shouldn’t put the Queue element in the todevice element class. After I move it out, Queue's push input port can be reused. Until now, I have finished creating the configuration to translate UDP and TCP flow. Tomorrow we will add DPDK device and maybe the ICMP protocl into the configuration and test if there is any error.

You can see the configurations in file Single_core_NAT_without_DPDK.click.

\-Hongyi & Lida

## 18-09-21

Finishing configuring NAT with DPDK device. At next stage we will test this NAT to prove the bottleneck performance.

\-Hongyi

## 18-09-22

Adding ICMP echo and echo reply. Maybe the click element document could add some more specific example for parameters. For this example, ICMPPingRewriter has the same input parameters as IPRewriter. Next few days we will add the rest ICMP protocol rewriter to finish all the NAT function.

\-Hongyi & Lida

## 18-09-23

Adding ICMP Rewriter. Until now, we finished all NAT function.

\-Lida

## 18-09-28

Upload DPDK-Forwarding.click. This file is used to test original performance by only forwarding packets without NAT function

\- Hongyi