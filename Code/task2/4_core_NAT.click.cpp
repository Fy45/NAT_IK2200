define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32
);

AddressInfo(
    left_interface     192.168.100.254    52:54:00:1e:4f:f3,
    right_interface    192.168.200.166    52:54:00:e3:70:30
);

// Module's I/O
nicIn0  :: FromDPDKDevice($iface0, BURST $burst);
nicOut0 :: ToDPDKDevice  ($iface0, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst);
nicOut1 :: ToDPDKDevice  ($iface1, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any other

arpq_left :: ARPQuerier(left_interface) -> nicOut0; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any Other

class_port_0 :: IPClassifier(dst port < 53884 && dst port > 49999, 
							dst port < 57768 && dst port > 53883, 
							dst port < 61650 && dst port > 57767, 
							dst port > 61649);
class_port_1 :: IPClassifier(dst port < 53884 && dst port > 49999, 
							dst port < 57768 && dst port > 53883, 
							dst port < 61650 && dst port > 57767, 
							dst port > 61649);
class_port_2 :: IPClassifier(dst port < 53884 && dst port > 49999, 
							dst port < 57768 && dst port > 53883, 
							dst port < 61650 && dst port > 57767, 
							dst port > 61649);
class_port_3 :: IPClassifier(dst port < 53884 && dst port > 49999, 
							dst port < 57768 && dst port > 53883, 
							dst port < 61650 && dst port > 57767, 
							dst port > 61649);

arpq_right :: ARPQuerier(right_interface) -> nicOut1; //The packet will go to right interface

ip_rw_l_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_1 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_2 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_3 :: IPClassifier(proto tcp, proto udp);

ip_rw_r_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_1 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_2 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_3 :: IPClassifier(proto tcp, proto udp);

rwpattern_0 :: IPRewriterPatterns(NAT_0 right_interface 50000-53883 - -);
rwpattern_1 :: IPRewriterPatterns(NAT_1 right_interface 53884-57767 - -);
rwpattern_2 :: IPRewriterPatterns(NAT_2 right_interface 57768-61649 - -);
rwpattern_3 :: IPRewriterPatterns(NAT_3 right_interface 61650-65535 - -);
tcp_rw_0 :: TCPRewriter(pattern NAT_0 0 1, pass 1);
udp_rw_0 :: UDPRewriter(pattern NAT_0 0 1, pass 1);

tcp_rw_1 :: TCPRewriter(pattern NAT_1 0 1, pass 1);
udp_rw_1 :: UDPRewriter(pattern NAT_1 0 1, pass 1);

tcp_rw_2 :: TCPRewriter(pattern NAT_2 0 1, pass 1);
udp_rw_2 :: UDPRewriter(pattern NAT_2 0 1, pass 1);

tcp_rw_3 :: TCPRewriter(pattern NAT_3 0 1, pass 1);
udp_rw_3 :: UDPRewriter(pattern NAT_3 0 1, pass 1);

Cpuleft :: CPUSwitch;
Pipleft :: Pipeliner(NOUSELESS true);
Cpuright :: CPUSwitch;
Pipright :: Pipeliner(NOUSELESS true);

Pip_0 :: Pipeliner(NOUSELESS true);
Pip_1 :: Pipeliner(NOUSELESS true);
Pip_2 :: Pipeliner(NOUSELESS true);
Pip_3 :: Pipeliner(NOUSELESS true);

nicIn0 -> class_left;

class_left[0] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> ARPResponder(left_interface) -> nicOut0;
class_left[1] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> [1]arpq_left;
class_left[2] -> Cpuleft;
Cpuleft[0] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_0;
Cpuleft[1] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_1;
Cpuleft[2] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_2;
Cpuleft[3] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_3;


ip_rw_l_0[0] -> [0]tcp_rw_0;    //Rewrite the packet and foward to right interface
ip_rw_l_0[1] -> [0]udp_rw_0;

ip_rw_l_1[0] -> [0]tcp_rw_1;    //Rewrite the packet and foward to right interface
ip_rw_l_1[1] -> [0]udp_rw_1;

ip_rw_l_2[0] -> [0]tcp_rw_2;    //Rewrite the packet and foward to right interface
ip_rw_l_2[1] -> [0]udp_rw_2;

ip_rw_l_3[0] -> [0]tcp_rw_3;    //Rewrite the packet and foward to right interface
ip_rw_l_3[1] -> [0]udp_rw_3;

tcp_rw_0[0] -> [0]Pipleft;
udp_rw_0[0] -> [1]Pipleft;
tcp_rw_1[0] -> [2]Pipleft;
udp_rw_1[0] -> [3]Pipleft;
tcp_rw_2[0] -> [4]Pipleft;
udp_rw_2[0] -> [5]Pipleft;
tcp_rw_3[0] -> [6]Pipleft;
udp_rw_3[0] -> [7]Pipleft;

Pipleft -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> [1]arpq_right;
class_right[2] -> Cpuright
Cpuright[0] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_0; 
Cpuright[1] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_1;
Cpuright[2] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_2;
Cpuright[3] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_3;

class_port_0[0] -> [0]Pip_0;
class_port_0[1] -> [0]Pip_1;
class_port_0[2] -> [0]Pip_2;
class_port_0[3] -> [0]Pip_3;

class_port_1[0] -> [1]Pip_0;
class_port_1[1] -> [1]Pip_1;
class_port_1[2] -> [1]Pip_2;
class_port_1[3] -> [1]Pip_3;

class_port_2[0] -> [2]Pip_0;
class_port_2[1] -> [2]Pip_1;
class_port_2[2] -> [2]Pip_2;
class_port_2[3] -> [2]Pip_3;

class_port_3[0] -> [3]Pip_0;
class_port_3[1] -> [3]Pip_1;
class_port_3[2] -> [3]Pip_2;
class_port_3[3] -> [3]Pip_3;

Pip_0 -> ip_rw_r_0;
Pip_1 -> ip_rw_r_1;
Pip_2 -> ip_rw_r_2;
Pip_3 -> ip_rw_r_3;

ip_rw_r_0[0] -> [1]tcp_rw_0;   //If we have the mapping, forward the packet to left interface
ip_rw_r_0[1] -> [1]udp_rw_0;

ip_rw_r_1[0] -> [1]tcp_rw_1;   //If we have the mapping, forward the packet to left interface
ip_rw_r_1[1] -> [1]udp_rw_1;

ip_rw_r_2[0] -> [1]tcp_rw_2;   //If we have the mapping, forward the packet to left interface
ip_rw_r_2[1] -> [1]udp_rw_2;

ip_rw_r_3[0] -> [1]tcp_rw_3;   //If we have the mapping, forward the packet to left interface
ip_rw_r_3[1] -> [1]udp_rw_3;

tcp_rw_0[1] -> [0]Pipright;
udp_rw_0[1] -> [1]Pipright;
tcp_rw_1[1] -> [2]Pipright;
udp_rw_1[1] -> [3]Pipright;
tcp_rw_2[1] -> [4]Pipright;
udp_rw_2[1] -> [5]Pipright;
tcp_rw_3[1] -> [6]Pipright;
udp_rw_3[1] -> [7]Pipright;

Pipright -> arpq_left[0] -> nicOut0;
