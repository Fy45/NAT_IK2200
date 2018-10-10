AddressInfo(
    ens34_in     192.168.56.128   192.168.56.0/24  00:0c:29:64:de:a1,
    ens35_out    10.1.0.128                        00:0c:29:64:de:ab,
    host_in      192.168.56.129                    00:0c:29:91:c6:7b
);



arp_class1 :: Classifier(12/0800);


pattern_in :: IPRewriterPatterns(NAT_out ens35_out - - -);

iprw1 :: IPRewriter(pattern NAT_out 0 0);

FromDevice(ens34) -> Tee -> Print(Before) -> arp_class1[0] -> Strip(14) -> CheckIPHeader
                         -> IPClassifier(src net ens34_in) ->  iprw1
                      -> Queue(1024) -> Print(After) -> PullTee -> ToDevice(ens35);