AddressInfo(
    left_interface     192.168.56.128      00:0c:29:64:de:a1,
    right_interface    10.1.0.128          00:0c:29:64:de:ab
);

fd_left :: FromDevice(ens34);
td_left :: Queue(1024) -> ToDevice(ens34);

fd_right :: FromDevice(ens35);
td_right :: Queue(1024) -> ToDevice(ens35);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                       	 12/0806 20/0002,  // ARP response
                       	 12/0800); //IP

arpq_left :: ARPQuerier(left_interface) -> td_left; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                       	 12/0806 20/0002,  // ARP response
                       	 12/0800); //IP

arpq_right :: ARPQuerier(right_interface) -> td_right; //The packet will go to right interface

ip_rw_l :: IPClassifier(proto tcp, proto udp);
ip_rw_r :: IPClassifier(proto tcp, proto udp);

rwpattern :: IPRewriterPatterns(NAT right_interface 50000-65535 - -);
tcp_rw :: TCPRewriter(pattern NAT 0 1, pass 1);
udp_rw :: UDPRewriter(pattern NAT 0 1, pass 1);

fd_left -> class_left;

class_left[0] -> ARPResponder(left_interface) -> td_left;
class_left[1] -> [1]arpq_left;
class_left[2] -> Strip(14)-> CheckIPHeader -> ip_rw_l;

ip_rw_l[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
ip_rw_l[1] -> [0]udp_rw;

tcp_rw[0] -> arpq_right[0] -> td_right;
udp_rw[0] -> arpq_right[0] -> td_right;


fd_right -> class_right;

class_right[0] -> ARPResponder(right_interface) -> td_right;
class_right[1] -> [1]arpq_right;
class_right[2] -> Strip(14)-> CheckIPHeader -> ip_rw_r;

ip_rw_r[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
ip_rw_r[1] -> [1]udp_rw;

tcp_rw[1] -> arpq_left[0] -> td_left;
udp_rw[1] -> arpq_left[0] -> td_left;