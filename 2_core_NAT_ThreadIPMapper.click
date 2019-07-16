define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32,
 $left_mac     52:54:00:1e:4f:f3,   //These MACs are based on the machine which we are going to use for Demo
 $left_if_mac  52:54:00:e9:a1:29,
 $right_mac    52:54:00:e3:70:30,
 $right_if_mac 52:54:00:3e:22:fb,

 $left_ip  192.168.100.254,
 $right_ip 192.168.200.166,
 $CPU       2
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
nicIn0  :: FromDPDKDevice($iface0, BURST $burst, SCALE parallel, MINTHREADS $CPU, VERBOSE 99, PROMISC true);
nicOut0 :: ToDPDKDevice  ($iface0, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst, SCALE parallel, MINTHREADS $CPU, VERBOSE 99, PROMISC true);
nicOut1 :: ToDPDKDevice  ($iface1, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any other

arpq_left :: EtherEncap(0x0800, $left_mac, $left_if_mac);

arpq_left -> nicOut0; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                          12/0806 20/0002,  // ARP response
                          12/0800); //Any Other

class_port_r :: IPClassifier(dst port < 37768 && dst port > 8000 , dst port > 37767);


arpq_right :: EtherEncap(0x0800, $right_mac, $right_if_mac);
arpq_right -> nicOut1; //The packet will go to right interface

ip_rw_l :: IPClassifier(proto tcp, proto udp);
ip_rw_r :: IPClassifier(proto tcp, proto udp);

NAT :: ThreadIPMapper($right_ip 8000-37767 - - 0 1,
                      $right_ip 37768-65535 - - 0 1);

tcp_rw :: TCPRewriter(NAT, pass 1);
udp_rw :: UDPRewriter(NAT, pass 1);



nicIn0 -> class_left;

class_left[0]  -> ARPResponder(left_interface) -> nicOut0;
class_left[1]  -> Discard;
class_left[2]  -> Strip(14)
               -> cip_l :: CheckIPHeader
               -> ip_rw_l;

ip_rw_l[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
ip_rw_l[1] -> [0]udp_rw;


tcp_rw[0] -> arpq_right -> nicOut1;
udp_rw[0] -> arpq_right -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> Discard;
class_right[2] -> Strip(14)-> CheckIPHeader -> class_port_r;

class_port_r[0] -> my_pipeliner_0 -> ip_rw_r;
class_port_r[1] -> my_pipeliner_1 -> ip_rw_r;

ip_rw_r[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
ip_rw_r[1] -> [1]udp_rw;

tcp_rw[1] -> arpq_left -> nicOut0;
udp_rw[1] -> arpq_left -> nicOut0;

//DriverManager(wait, read nicIn0.xstats, read nicIn1.xstats);
