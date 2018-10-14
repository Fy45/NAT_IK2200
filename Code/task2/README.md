## 18-10-14

Until now I have finished the NAT for multi-core support based on software classification method. There are three files during the development which also represent three stages of the development. 

First is to write a simple forwarding configuration with multi-core supported. This requires to duplicate and handle the session for ARP query and response.

Second is to duplicate the NAT function based on the previous stage. The problem is to send the packets to the correct Rewrite element based on their destination port. Otherwise, generate will never receive any ACK from Sink machine since all the return packets will be dropped by the NAT.

Third is to extend the 2-core script to 4-core. You can see all the script in this folder

\-Hongyi
