from trex_stl_lib.api import *

class STLS1(object):
    """
    Create flow stat stream of UDP packet.
    Can specify using tunables following params:
      Packet length (fsize)
      Packet group id (pg_id)
      Packet type(pkt_type)
      Number of streams (num_streams)
    """
    def __init__ (self):
        self.fsize = 64
        self.pg_id = 0
        self.num_streams = 1
        self.dport=12
        self.sport=1025
        self.pps=100

    def _create_stream (self):
        size = self.fsize - 4; # HW will add 4 bytes ethernet CRC
        pkt0=[]
        pkt1=[]
        for port_add in range(0,self.num_streams):
          base_pkt0 = Ether() / IP(src = "192.168.100.157", dst = "192.168.200.175") / UDP(dport = self.dport+port_add, sport = 1025)
          base_pkt1 = Ether() / IP(src = "192.168.100.157", dst = "192.168.200.175") / UDP(dport = 12, sport = self.dport+port_add)
          pad0 = max(0, size - len(base_pkt0)) * 'x'
          pad1 = max(0, size - len(base_pkt1)) * 'x'
          pkt0.append(STLPktBuilder(pkt = base_pkt0/pad0))
          pkt1.append(STLPktBuilder(pkt = base_pkt1/pad1))


        streams = []
        streams.append(STLStream(packet = pkt0[0], mode = STLTXCont(pps=1), flow_stats = STLFlowLatencyStats(pg_id = self.pg_id)))
        streams.append(STLStream(packet = pkt0[1], mode = STLTXCont(pps=1), flow_stats = STLFlowStats(pg_id = self.pg_id+1)))
        for pkt_num in range(0, self.num_streams):
            streams.append(STLStream(packet = pkt0[pkt_num], mode = STLTXCont(pps=self.pps)))
            streams.append(STLStream(packet = pkt1[pkt_num], mode = STLTXCont(pps=self.pps)))

        return streams

    def get_streams (self, fsize = 64, pg_id = 0,  num_streams = 1,dport_num=12,sport_num=1025,pps_num=100, **kwargs):
        self.fsize = fsize
        self.pg_id = pg_id
        self.num_streams = num_streams
        self.dport=dport_num
        self.sport=sport_num
        self.pps=pps_num
        return self._create_stream()

# dynamic load - used for trex console or simulator
def register():
    return STLS1()
