AddressInfo(
    ens34_in     192.168.56.128   192.168.56.0/24  00:0c:29:64:de:a1,
    ens35_out    10.1.0.128                        00:0c:29:64:de:ab,
    host_in      192.168.56.129                    00:0c:29:91:c6:7b
);

elementclass fromdevice {
  $device |
  from :: FromDevice($device)
    -> t1 :: Tee
    -> output;
  ScheduleInfo(from .1, to 1);
}

elementclass todevice {
  $device |
  input -> q :: Queue(1024)
    -> t2 :: PullTee
    -> to :: ToDevice($device);
  ScheduleInfo(from .1, to 1);
}


pk_classify :: Classifier(12/0806 20/0001,
                        12/0806 20/0002,
                        12/0800);

pattern_in :: IPRewriterPatterns(NAT_out ens35_out - - -);
arpquery :: ARPQuerier(ens34_in) -> todevice(ens34);

fromdevice(ens34) ->  pk_classify;
fromdevice(ens35) ->  pk_classify;

ip_to_host :: EtherEncap(0x800, host_in, ens35_out) -> todevice(ens35);
ip_to_intern :: GetIPAddress(16) -> CheckIPHeader -> arpquery;

pk_classify[0] -> ARPResponder(ens34_in, ens35_out) -> todevice(ens34);

pk_classify[1] -> arp_t :: Tee;
arp_t[0] ->  todevice(ens34);
arp_t[1] -> [1]arpquery;

pk_classify[2] -> Strip(14)-> CheckIPHeader 
	-> ipclass :: IPClassifier(dst host ens35_out,
                               dst host ens34_in,
                               src net ens34_in);

iprw :: IPRewriterPatterns(NAT ens35_out 50000-65535 - -);
rw :: IPRewriter(pattern NAT 0 1, pass 1);

ipclass[0] -> [1]rw;

rw[0] ->  GetIPAddress(16) -> CheckIPHeader -> EtherEncap(0x800, ens35_out, host_in) -> todevice(ens35);

rw[1] -> established_class :: IPClassifier(dst host ens35_out,
                                           dst net ens34_in);

established_class[0] -> ip_to_host;
established_class[1] -> ip_to_intern;

ipclass[1] -> IPClassifier(src net ens34_in) -> ip_to_host;

ipclass[2] -> inter_class :: IPClassifier(dst net ens34_in, -);
inter_class[0] -> ip_to_intern;
inter_class[1] -> ip_udp_class :: IPClassifier(tcp or udp);
ip_udp_class[0] -> [0]rw;

