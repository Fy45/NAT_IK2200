AddressInfo(
    ens34_in     192.168.56.128   192.168.56.0/24  00:0c:29:64:de:a1,
    ens35_out    10.1.0.128                        00:0c:29:64:de:ab,
    host_in      192.168.56.129                    00:0c:29:91:c6:7b
);

pattern_in :: IPRewriterPatterns(NAT_out ens35_out - - -);
pattern_out :: IPRewriterPatterns(NAT_in - - host_in -);
iprw1 :: IPRewriter(pattern NAT_out 0 0);
iprw2 :: IPRewriter(pattern NAT_in 0 0);

FromDevice(ens34) -> Print(Before)-> Tee -> iprw1 -> Queue -> PullTee -> Print(After) -> ToDevice(ens35);
FromDevice(ens35) -> Tee -> iprw2 -> Queue -> PullTee -> ToDevice(ens34);