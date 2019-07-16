/*
* This original script didn’t use ThreadIPMapper, therefore multiple rewriter elements should be used.
* Please see another ThreadIPMapper version.
*
*/

define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32

 $left_mac     52:54:00:7f:78:46,   //These MACs are based on the machine which we are going to use for Demo
 $left_if_mac  52:54:00:62:68:b1,
 $right_mac    52:54:00:e0:67:cb,
 $right_if_mac 52:54:00:75:a7:dc,

 $left_ip  192.168.100.254,
 $right_ip 192.168.200.166

);

AddressInfo(
    left_interface     $left_ip     $left_mac, 
    right_interface    $right_ip    $right_mac
);

my_pipeliner_0 :: Pipeliner;
my_pipeliner_1 :: Pipeliner;

StaticThreadSched(my_pipeliner_0 0);
StaticThreadSched(my_pipeliner_1 1);


// Module's I/O
nicIn0  :: FromDPDKDevice($iface0, BURST $burst, SCALE parallel, VERBOSE 99, PROMISC true);
nicOut0 :: ToDPDKDevice  ($iface0, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst, SCALE parallel, VERBOSE 99, PROMISC true);
nicOut1 :: ToDPDKDevice  ($iface1, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any other


arpq_left :: EtherEncap(0x0800, $left_mac, $left_if_mac) -> nicOut0; //The packet will go to left interface


class_right :: Classifier(12/0806 20/0001,  //ARP query
                          12/0806 20/0002,  // ARP response
                          12/0800); //Any Other

CPULeft :: CPUSwitch;

class_port_r :: IPClassifier(dst port < 37768 && dst port > 8000 , dst port > 37767);

arpq_right :: EtherEncap(0x0800, $right_mac, $right_if_mac) -> nicOut1; //The packet will go to right interface

ip_rw_l_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_l_1 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_0 :: IPClassifier(proto tcp, proto udp);
ip_rw_r_1 :: IPClassifier(proto tcp, proto udp);

rwpattern_0 :: IPRewriterPatterns(NAT_0 right_interface 8000-37767 - -);
rwpattern_1 :: IPRewriterPatterns(NAT_1 right_interface 37768-65535 - -);

tcp_rw_0 :: TCPRewriter(pattern NAT_0 0 1, pass 1);
udp_rw_0 :: UDPRewriter(pattern NAT_0 0 1, pass 1);

tcp_rw_1 :: TCPRewriter(pattern NAT_1 0 1, pass 1);
udp_rw_1 :: UDPRewriter(pattern NAT_1 0 1, pass 1);


nicIn0 -> class_left;

class_left[0]  -> ARPResponder(left_interface) -> nicOut0;
class_left[1]  -> Discard;
class_left[2] -> Strip(14)-> CheckIPHeader -> CPULeft;

CPULeft[0] -> ip_rw_l_0;
CPULeft[1] -> ip_rw_l_1;

ip_rw_l_0[0] -> [0]tcp_rw_0;    //Rewrite the packet and foward to right interface
ip_rw_l_0[1] -> [0]udp_rw_0;

ip_rw_l_1[0] -> [0]tcp_rw_1;    //Rewrite the packet and foward to right interface
ip_rw_l_1[1] -> [0]udp_rw_1;

tcp_rw_0[0] -> arpq_right -> nicOut1;
udp_rw_0[0] -> arpq_right -> nicOut1;
tcp_rw_1[0] -> arpq_right -> nicOut1;
udp_rw_1[0] -> arpq_right -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> Discard;
class_right[2] -> Strip(14)-> CheckIPHeader -> class_port_r;

class_port_r[0] -> my_pipeliner_0 -> ip_rw_r_0;
class_port_r[1] -> my_pipeliner_1 -> ip_rw_r_1;

ip_rw_r_0[0] -> [1]tcp_rw_0;   //If we have the mapping, forward the packet to left interface
ip_rw_r_0[1] -> [1]udp_rw_0;

ip_rw_r_1[0] -> [1]tcp_rw_1;   //If we have the mapping, forward the packet to left interface
ip_rw_r_1[1] -> [1]udp_rw_1;

tcp_rw_0[1] -> arpq_left -> nicOut0;
udp_rw_0[1] -> arpq_left -> nicOut0;

tcp_rw_1[1] -> arpq_left -> nicOut0;
udp_rw_1[1] -> arpq_left -> nicOut0;
