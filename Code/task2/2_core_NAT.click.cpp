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

class_port_0 :: IPClassifier(dst port < 57768, dst port > 57767);
class_port_1 :: IPClassifier(dst port < 57768, dst port > 57767);

arpq_right :: ARPQuerier(right_interface) -> nicOut1; //The packet will go to right interface

ip_rw_l_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_1 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_1 :: IPClassifier(proto tcp, proto udp);

rwpattern_0 :: IPRewriterPatterns(NAT_0 right_interface 50000-57767 - -);
rwpattern_1 :: IPRewriterPatterns(NAT_1 right_interface 57768-65535 - -);
tcp_rw_0 :: TCPRewriter(pattern NAT_0 0 1, pass 1);
udp_rw_0 :: UDPRewriter(pattern NAT_0 0 1, pass 1);

tcp_rw_1 :: TCPRewriter(pattern NAT_1 0 1, pass 1);
udp_rw_1 :: UDPRewriter(pattern NAT_1 0 1, pass 1);

Cpuleft :: CPUSwitch;
Pipleft :: Pipeliner(NOUSELESS true);
Cpuright :: CPUSwitch;
Pipright :: Pipeliner(NOUSELESS true);

Pip_0 :: Pipeliner(NOUSELESS true);
Pip_1 :: Pipeliner(NOUSELESS true);

nicIn0 -> class_left;

class_left[0] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> ARPResponder(left_interface) -> nicOut0;
class_left[1] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> [1]arpq_left;
class_left[2] -> Cpuleft;
Cpuleft[0] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_0;
Cpuleft[1] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> ip_rw_l_1;


ip_rw_l_0[0] -> [0]tcp_rw_0;    //Rewrite the packet and foward to right interface
ip_rw_l_0[1] -> [0]udp_rw_0;

ip_rw_l_1[0] -> [0]tcp_rw_1;    //Rewrite the packet and foward to right interface
ip_rw_l_1[1] -> [0]udp_rw_1;

tcp_rw_0[0] -> [0]Pipleft;
udp_rw_0[0] -> [1]Pipleft;
tcp_rw_1[0] -> [2]Pipleft;
udp_rw_1[0] -> [3]Pipleft;

Pipleft -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> CPUSwitch -> Pipeliner(NOUSELESS true) -> [1]arpq_right;
class_right[2] -> Cpuright
Cpuright[0] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_0; 
Cpuright[1] -> Pipeliner(NOUSELESS true) -> Strip(14)-> CheckIPHeader -> class_port_1;

class_port_0[0] -> [0]Pip_0;
class_port_0[1] -> [0]Pip_1;

class_port_1[0] -> [1]Pip_0;
class_port_1[1] -> [1]Pip_1;

Pip_0 -> ip_rw_r_0;
Pip_1 -> ip_rw_r_1;

ip_rw_r_0[0] -> [1]tcp_rw_0;   //If we have the mapping, forward the packet to left interface
ip_rw_r_0[1] -> [1]udp_rw_0;

ip_rw_r_1[0] -> [1]tcp_rw_1;   //If we have the mapping, forward the packet to left interface
ip_rw_r_1[1] -> [1]udp_rw_1;

tcp_rw_0[1] -> [0]Pipright;
udp_rw_0[1] -> [1]Pipright;
tcp_rw_1[1] -> [2]Pipright;
udp_rw_1[1] -> [3]Pipright;

Pipright -> arpq_left[0] -> nicOut0;
