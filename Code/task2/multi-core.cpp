define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32
);

AddressInfo(
    left_interface     192.168.56.128     00:0c:29:64:de:a1,
    right_interface    10.1.0.128         00:0c:29:64:de:ab
);

my_pipeliner_0 :: Pipeliner;
my_pipeliner_1 :: Pipeliner;

my_pipeliner_l_0 :: Pipeliner;
my_pipeliner_l_1 :: Pipeliner;

StaticThreadSched(my_pipeliner_0 0);
StaticThreadSched(my_pipeliner_1 1);

//StaticThreadSched(my_pipeliner_l_0 0);
//StaticThreadSched(my_pipeliner_l_1 1);

// Module's I/O
nicIn0  :: FromDPDKDevice($iface0, BURST $burst);
nicOut0 :: ToDPDKDevice  ($iface0, NDESC 512, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst);
nicOut1 :: ToDPDKDevice  ($iface1, NDESC 512, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any other

arpq_left :: ARPQuerier(left_interface) -> nicOut0; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any Other

//class_port_l :: IPClassifier(src port < 52767, src port > 52766);
class_port_r :: IPClassifier(dst port < 52767, dst port > 52766);

arpq_right :: ARPQuerier(right_interface) -> nicOut1; //The packet will go to right interface

ip_rw_l_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_1 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_1 :: IPClassifier(proto tcp, proto udp);

rwpattern_0 :: IPRewriterPatterns(NAT right_interface - - -);
tcp_rw :: TCPRewriter(pattern NAT 0 1, pass 1);
udp_rw :: UDPRewriter(pattern NAT 0 1, pass 1);

Cpuleft :: CPUSwitch;

nicIn0 -> class_left;

class_left[0] -> ARPResponder(left_interface) -> nicOut0;
class_left[1] -> [1]arpq_left;
class_left[2] -> Strip(14)-> CheckIPHeader -> ip_rw_l_0;
//class_port_l[0] -> ip_rw_l_0; //this is enough on master branch
//class_port_l[1] -> ip_rw_l_1;


ip_rw_l_0[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
ip_rw_l_0[1] -> [0]udp_rw;

//ip_rw_l_1[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
//ip_rw_l_1[1] -> [0]udp_rw;

tcp_rw[0] -> arpq_right[0] -> nicOut1;
udp_rw[0] -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> [1]arpq_right;
class_right[2] -> Strip(14)-> CheckIPHeader -> class_port_r;

class_port_r[0] -> my_pipeliner_0 -> ip_rw_r_0;
class_port_r[1] -> my_pipeliner_1 -> ip_rw_r_0;

ip_rw_r_0[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
ip_rw_r_0[1] -> [1]udp_rw;

//ip_rw_r_1[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
//ip_rw_r_1[1] -> [1]udp_rw;

tcp_rw[1] -> arpq_left[0] -> nicOut0;
udp_rw[1] -> arpq_left[0] -> nicOut0;