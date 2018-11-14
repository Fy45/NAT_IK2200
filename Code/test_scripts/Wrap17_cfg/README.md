## 18-10-30

Due to the limitation in speed of our current generator, we found another generator named [warp17](https://github.com/Juniper/warp17) to generate the packets traffics.

The detailed introduction and usage are shown in the link, here we explain about the CLI command in our cases.

To realize a TCP/UDP connection using *warp17*:

* __Add L3 interfaces__: configure an IP interface with the specified `ip` address and `mask` here we need to make sure the subnet of each port is consistent with the related interface of the middle machine. 

```
	e.g.:
	add tests l3_intf port 0 ip 192.168.100.177 mask 255.255.255.0 (as client/generator)
	add tests l3_intf port 1 ip 192.168.200.177 mask 255.255.255.0 (as server/sink)
```

* __Add L3 default gateway__: configure 'gw' as the default gateway for `eth_port`. 

	```
	add tests l3_gw port 0 gw 192.168.100.254
	add tests l3_gw port 1 gw 192.168.200.166
	```
* __Configure server test cases__: configure a server test case with ID `test-case-id` on `eth_port`. The underlying L4 traffic can be TCP or UDP. `ip_range` and `port_range` define the `<ip:port>` sockets on which the servers will be listening. 

	```
	add tests server tcp|udp port 1 test-case-id 0
					 src 192.168.200.177 192.168.200.177
					 sport 10000|1025
	```

* __Configure client test cases (per port)__: configure a client test case with ID `test-case-id` on `eth_port`. The source IP/l4-port and destination IP/l4-port ranges define the `<src_ip, src_port:dst_ip, dst_port>` TCP/UDP connections that will be established. 

	```
	add tests client tcp|udp port 0 test-case-id 0
	                 src 192.168.100.177 192.168.100.177
	                 sport 10001|1026 10001|1026
	                 dest 192.168.200.177 192.168.200.177
	                 dport 10000|1025 10000|1025
	```
* __Configure test profile parameters__: After the basic setup of the port we need to clearify the connection parameters in a profile:
	- __initial delay__ : we want to start the connection right away, so the delay time is 0
	
	```
	set tests timeouts port 0 test-case-id 0 init 0
	```
	- __rate__: the data rate defines client to send traffic on __per second__. `infinite` removes any rate limiting for sending traffic (i.e., WARP17 will try to do it as fast as possible)
	
	```
	set tests rate port 0 test-case-id 0 send 500000|infinite
	```
	- __run time__: defines the test case with 100s run-time of a certain connection.

	```
	set tests criteria port 0 test-case-id 0 run-time 100
	```
* __latency__: there are two ways to enable the computation of latency, in our case, we apply the raw timestamping both in TCP/UDP traffics. 
	1. `max` latency threshold defines all the incoming packets with a measured latency higher than the configured `max` will be counted as _threshold violations_; 
	2. `max-avg` latency threshold means every time the average measured latency is over the configured `max-avg` a new _threshold violation_ will be counted; 
	3. `samples` count: the number of __recent__ samples used for computing recent statistics. __Global__ statistics are computed per test case using all the received samples (not only the most recent ones)
	
	```
	set tests latency port 0|1 test-case-id 0 max 80 max-avg 40 samples 1000
	
	```
* __Raw application traffic__: this command emulates _request_ and _response_ traffic. The clients sends a request packet of a fixed configured size and waits for a fixed size response packet from the server.  

```
set tests client|server raw port 0|1 test-case-id 0 data-req-plen 64 data-resp-plen 0 (no latency enabled)
set tests client|server raw port 0|1 test-case-id 0 data-req-plen 64 data-resp-plen 16 rx-timestamp tx-timestamp (latency enabled)
``` 	
	
If `rx-timestamp` is set, the Warp17 traffic engine will timestamp packets at ingress and the RAW application will compute latency statistics when incoming packets have TX timestamp information embedded in their payload. 

If `tx-timestamp` is set RAW application clients will embed TX timestamps in the first 16 bytes of the application payload. The RX/TX timestamps are both computed early in the packet loop in order to be as precise as possible when measuring latency.
  
After the settings, we can `start tests port 0|1` and `show tests ui` to view the real-time traffic changes. All the CLI commands can be stored in to a configuration file in *.cfg* format. Then we can start the warp17 server using the `./build/warp17 -c 0xf -n 1 -m 10240 -- --tcb-pool-sz 10240 --cmd-file=exmaples/name_of_test.cfg` to start.

<!--
- __Configure tests as asynchronous__: if multiple test cases are defined on
  the same `eth_port`, by default, they will be executed in sequence (when a
  test case ends the next one is started). To change the behaviour the user can
  mark a test case as _async_ forcing the test engine to advance to the next
  configured test case without waiting for the current one to finish.

	```
	set tests async port 0 test-case-id <0|1|2...>
	```
	
-->
There are many others commands that we can use to show statistic and operational information all can be found at github [warp17](https://github.com/Juniper/warp17).

Still has some work on this generator...