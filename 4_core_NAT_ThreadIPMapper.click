/*
 * This 4-core nat can work for 1 to 4 cores, just change the end of the parameters of the following line :
 * click --dpdk -l 0-3 -w 0000:03:00.0 -w 0000:82:00.1 -- 4_core_NAT_ThreadIPMapper.click CPU=4 CPU1=1 CPU2=1 CPU3=1 CPU4=1 
 * -l specify cores going to use, -w declare the device identification
 * 
 */


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
 $CPU       4,
 $CPU1      true,
 $CPU2      true,
 $CPU3      true,
 $CPU4      true,
);

AddressInfo(
    left_interface     $left_ip     $left_mac, 
    right_interface    $right_ip    $right_mac,
);

my_pipeliner_0 :: Pipeliner(ACTIVE $CPU1);
my_pipeliner_1 :: Pipeliner(ACTIVE $CPU2);
my_pipeliner_2 :: Pipeliner(ACTIVE $CPU3);
my_pipeliner_3 :: Pipeliner(ACTIVE $CPU4);

StaticThreadSched(my_pipeliner_0 0);
StaticThreadSched(my_pipeliner_1 1);
StaticThreadSched(my_pipeliner_2 2);
StaticThreadSched(my_pipeliner_3 3);


// Module's I/O
nicIn0  :: FromDPDKDevice($iface0, BURST $burst, SCALE parallel, MINTHREADS $CPU, VERBOSE 99, PROMISC true);
nicOut0 :: ToDPDKDevice  ($iface0, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst, SCALE parallel, MINTHREADS $CPU, VERBOSE 99, PROMISC true);
nicOut1 :: ToDPDKDevice  ($iface1, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //Any other

arpq_left :: EtherEncap(0x0800, $left_mac, $left_if_mac);
//arpq_left :: ARPQuerier(left_interface)

arpq_left -> nicOut0; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                          12/0806 20/0002,  // ARP response
                          12/0800); //Any Other
class_port_r :: IPClassifier(dst port > 20000 && dst port < 30000 ,
                            dst port > 30000 && dst port < 40000 ,
                            dst port > 40000 && dst port < 50000 ,
                            dst port > 50000 && dst port < 60000
                            );


arpq_right :: EtherEncap(0x0800, $right_mac, $right_if_mac);
//arpq_right :: ARPQuerier(right_interface)
arpq_right -> nicOut1; //The packet will go to right interface

ip_rw_l :: IPClassifier(proto tcp, proto udp);
ip_rw_r :: IPClassifier(proto tcp, proto udp);

NAT :: ThreadIPMapper($right_ip 20000-30000 - - 0 1,
                      $right_ip 30000-40000 - - 0 1,
                      $right_ip 40000-50000 - - 0 1,
                      $right_ip 50000-60000 - - 0 1);

tcp_rw :: TCPRewriter(NAT, pass 1);
udp_rw :: UDPRewriter(NAT, pass 1);



nicIn0 -> class_left;

class_left[0]  -> ARPResponder(left_interface) -> nicOut0;
class_left[1]  -> Discard; //[1]arpq_left;
class_left[2]  -> Strip(14)
               -> cip_l :: CheckIPHeader
               -> ip_rw_l;

ip_rw_l[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
ip_rw_l[1] -> [0]udp_rw;


tcp_rw[0] -> arpq_right[0] -> nicOut1;
udp_rw[0] -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> Discard; //[1]arpq_right;
class_right[2] -> Strip(14)-> CheckIPHeader -> class_port_r;

class_port_r[0] -> my_pipeliner_0 -> ip_rw_r;
class_port_r[1] -> my_pipeliner_1 -> ip_rw_r;
class_port_r[2] -> my_pipeliner_2 -> ip_rw_r;
class_port_r[3] -> my_pipeliner_3 -> ip_rw_r;

ip_rw_r[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
ip_rw_r[1] -> [1]udp_rw;

tcp_rw[1] -> arpq_left[0] -> nicOut0;
udp_rw[1] -> arpq_left[0] -> nicOut0;

//DriverManager(wait, read nicIn0.xstats, read nicIn1.xstats);
