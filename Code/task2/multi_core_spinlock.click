define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32
);
HTTPServer;

AddressInfo(
    left_interface     192.168.104.128     00:0c:29:17:ec:a2,
    right_interface    172.16.216.128     00:0c:29:17:ec:ac
);

SpinlockPattern :: SpinlockInfo(lock_1, lock_2);

// Module's I/O
nicIn0  :: FromDPDKDevice($iface0, BURST $burst);
nicOut0 :: ToDPDKDevice  ($iface0, NDESC 512, IQUEUE $queueSize, BURST $burst);

nicIn1  :: FromDPDKDevice($iface1, BURST $burst);
nicOut1 :: ToDPDKDevice  ($iface1, NDESC 512, IQUEUE $queueSize, BURST $burst);

class_left :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //IP

arpq_left :: ARPQuerier(left_interface) -> nicOut0; //The packet will go to left interface

class_right :: Classifier(12/0806 20/0001,  //ARP query
                         12/0806 20/0002,  // ARP response
                         12/0800); //IP

arpq_right :: ARPQuerier(right_interface) -> nicOut1; //The packet will go to right interface

ip_rw_l :: IPClassifier(proto tcp, proto udp);
ip_rw_r :: IPClassifier(proto tcp, proto udp);

rwpattern :: IPRewriterPatterns(NAT right_interface 50000-65535 - -);
tcp_rw :: TCPRewriter(pattern NAT 0 1, pass 1);
udp_rw :: UDPRewriter(pattern NAT 0 1, pass 1);

nicIn0 -> class_left;

class_left[0] -> ARPResponder(left_interface) -> nicOut0;
class_left[1] -> [1]arpq_left;
class_left[2] -> SpinlockAcquire(lock_1) -> Strip(14) -> CheckIPHeader -> ip_rw_l;

ip_rw_l[0] -> [0]tcp_rw;    //Rewrite the packet and foward to right interface
ip_rw_l[1] -> [0]udp_rw;

tcp_rw[0] -> SpinlockRelease(lock_1) -> arpq_right[0] -> nicOut1;
udp_rw[0] -> SpinlockRelease(lock_1) -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> [1]arpq_right;
class_right[2] ->  SpinlockAcquire(lock_2) -> Strip(14)-> CheckIPHeader -> ip_rw_r;

ip_rw_r[0] -> [1]tcp_rw;   //If we have the mapping, forward the packet to left interface
ip_rw_r[1] -> [1]udp_rw;


tcp_rw[1] -> SpinlockRelease(lock_2) -> arpq_left[0] -> nicOut0;
udp_rw[1] -> SpinlockRelease(lock_2) -> arpq_left[0] -> nicOut0;
