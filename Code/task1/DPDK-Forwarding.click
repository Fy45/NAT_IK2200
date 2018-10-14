define(
 $iface0    0,
 $iface1    1,
 $queueSize 1024,
 $burst     32
);

AddressInfo(
    left_interface     192.168.104.128    00:0c:29:17:ec:a2,
    right_interface    172.16.216.128    00:0c:29:17:ec:ac
);

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

arpq_right :: ARPQuerier(right_interface) -> nicOut1; //The packet will go to right interface


nicIn0 -> class_left;

class_left[0] -> ARPResponder(left_interface) -> nicOut0;
class_left[1] -> [1]arpq_left;
class_left[2] -> Strip(14)-> CheckIPHeader -> arpq_right[0] -> nicOut1;

nicIn1 -> class_right;

class_right[0] -> ARPResponder(right_interface) -> nicOut1;
class_right[1] -> [1]arpq_right;
class_right[2] -> Strip(14)-> CheckIPHeader -> arpq_left[0] -> nicOut0;
