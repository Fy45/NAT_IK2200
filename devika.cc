#include <click/config.h>
#include "devika.hh"
#include <click/args.hh>
#include <click/straccum.hh>
#include <click/error.hh>
#include <click/timer.hh>
#include <clicknet/tcp.h>
#include <clicknet/udp.h>
#include <rte_hash.h>
CLICK_DECLS



devika::devika() : _allocator()
{
}

devika::~devika()
{
}

void *
devika::cast(const char *n)
{
    if (strcmp(n, "IPRewriterBase") == 0)
	return (IPRewriterBase *)this;
    else if (strcmp(n, "devika") == 0)
	return (devika *)this;
    else
	return 0;
}

int
devika::configure(Vector<String> &conf, ErrorHandler *errh)
{
    bool dst_anno = true, has_reply_anno = false,
	has_udp_streaming_timeout, has_streaming_timeout;
    int reply_anno;
    uint32_t timeouts[2];
    timeouts[0] = 300;		// 5 minutes
    timeouts[1] = default_guarantee;

    if (Args(this, errh).bind(conf)
	.read("DST_ANNO", dst_anno)
	.read("REPLY_ANNO", AnnoArg(1), reply_anno).read_status(has_reply_anno)
	.read("UDP_TIMEOUT", SecondsArg(), timeouts[0])
	.read("TIMEOUT", SecondsArg(), timeouts[0])
	.read("UDP_STREAMING_TIMEOUT", SecondsArg(), _udp_streaming_timeout).read_status(has_udp_streaming_timeout)
	.read("STREAMING_TIMEOUT", SecondsArg(), _udp_streaming_timeout).read_status(has_streaming_timeout)
	.read("UDP_GUARANTEE", SecondsArg(), timeouts[1])
	.consume() < 0)
	return -1;

    for (unsigned i=0; i<_mem_units_no; i++) {
        _timeouts[i][0] = timeouts[0];
        _timeouts[i][1] = timeouts[1];
    }

    _annos = (dst_anno ? 1 : 0) + (has_reply_anno ? 2 + (reply_anno << 2) : 0);
    if (!has_udp_streaming_timeout && !has_streaming_timeout) {
        for (int i = 0; i < _mem_units_no; i++) {
            _udp_streaming_timeout = _timeouts[i][0];
        }
    }
    _udp_streaming_timeout *= CLICK_HZ; // IPRewriterBase handles the others


    //setup hash
    struct rte_hash_parameters ipv4_hash_params;
    /*{
        .name = NULL,
        .entries = HASH_ENTRIES,
        .key_len = sizeof(struct ipv4_5tuple),
        .hash_func = DEFAULT_HASH_FUNC,
        .hash_func_init_val = 0,
    };*/

    ipv4_hash_params.name = "hash_table";
    ipv4_hash_params.entries = HASH_ENTRIES;
    ipv4_hash_params.key_len = sizeof(struct ipv4_5tuple);
    ipv4_hash_params.hash_func = DEFAULT_HASH_FUNC;
    ipv4_hash_params.hash_func_init_val = 0;
    ipv4_hash_params.socket_id = 0;
    nat_lookup_struct = rte_hash_create(&ipv4_hash_params);
    if (nat_lookup_struct == NULL)
        rte_exit(EXIT_FAILURE, "Unablea to create the hash table on sockets %d\n", 1);
    printf("%s\n", "create hash");
    //end setup hash
    return IPRewriterBase::configure(conf, errh);
}




         
int
devika::process(int port, Packet *p_in)
{
    WritablePacket *p = p_in->uniqueify();
    if (!p) {
        return -2;
    }

    click_ip *iph = p->ip_header();

    /* handle non-TCP and non-first fragments */
    int ip_p = iph->ip_p;
    if ((ip_p != IP_PROTO_TCP && ip_p != IP_PROTO_UDP && ip_p != IP_PROTO_DCCP)
	|| !IP_FIRSTFRAG(iph)
	|| p->transport_length() < 8) {
        const IPRewriterInput &is = _input_specs[port];
        if (is.kind == IPRewriterInput::i_nochange)
            return is.foutput;
        else
            return -1;
    }
    /* hash         */
    struct ipv4_5tuple myflow;
    myflow.ip_src = iph->ip_src;
    myflow.ip_dst = iph->ip_dst;
    myflow.proto = iph->ip_p;
    click_udp *udph = p->udp_header();
    //if (ip_p == IP_PROTO_UDP){
        myflow.port_src=udph->uh_sport;
        myflow.port_dst=udph->uh_dport;
    //}
    
    int ret;
    if(port==0){ /*do NAT (from inside to outside)*/
        ret = rte_hash_lookup(nat_lookup_struct, (const void *)&myflow);
        if(ret<0){ /*See this flow for the first time*/
            /* TODO: allocate ip & port from pool*/
            in_addr public_ip;
            public_ip.s_addr = htonl(IPv4(192, 168, 3, 1));
            uint16_t public_port = udph->uh_sport; //htons()

            /*Add this flow to NAT table*/
            ret = rte_hash_add_key (nat_lookup_struct, 
                        (void *) &myflow);
            if (ret < 0) {
                    rte_exit(EXIT_FAILURE, "Unable to add entry (inside)\n");
            }
            nat_table[ret].ip = public_ip;
            nat_table[ret].port = public_port;
                       
            myflow.ip_src = iph->ip_dst;
            myflow.ip_dst = public_ip;
            myflow.port_src = udph->uh_dport;
            myflow.port_dst = public_port;

            ret = rte_hash_add_key (nat_lookup_struct,
                        (void *) &myflow);
            if (ret < 0) {
                    rte_exit(EXIT_FAILURE, "Unable to add entry (outside)\n");
            }
            
            nat_table[ret].ip = iph->ip_src;
            nat_table[ret].port = udph->uh_sport;

            /*change packet field*/
            iph->ip_src = public_ip;
            udph->uh_sport = public_port;
        }
        else{
            /*change packet field*/
	    iph->ip_src = nat_table[ret].ip;
            udph->uh_sport = nat_table[ret].port;
        }
        
    	return 0;
    }
    else{/*undo nat (from outside to inside)*/
	ret = rte_hash_lookup(nat_lookup_struct, (const void *)&myflow);
        if(ret<0){ /*See this flow for the first time so drop it */
        	/*TODO: How to realy drop a packet?*/
        	printf("%s\n", "can not find flow");
        	return -1;
        }
        else{
            /*change packet field*/
            
            iph->ip_dst = nat_table[ret].ip;
            udph->uh_dport = nat_table[ret].port;
            p->set_dst_ip_anno(nat_table[ret].ip);
        
        }

    	return 1;
    }
}

void
devika::push(int port, Packet *p)
{
    int output_port = process(port, p);
    if (output_port < 0) {
        if (likely(output_port) == -1)
            p->kill();
        return;
    }
    
    checked_output_push(output_port, p);
}

#if HAVE_BATCH
void
devika::push_batch(int port, PacketBatch *batch)
{
    auto fnt = [this,port](Packet*p){return process(port,p);};
    CLASSIFY_EACH_PACKET(noutputs() + 1,fnt,batch,checked_output_push_batch);
}
#endif

String
devika::dump_mappings_handler(Element *e, void *)
{
    devika *rw = (devika *)e;
    click_jiffies_t now = click_jiffies();
    StringAccum sa;
    for (int i = 0; i < rw->_mem_units_no; i++) {
        for (Map::iterator iter = rw->_map[i].begin(); iter.live(); ++iter) {
            iter->flow()->unparse(sa, iter->direction(), now);
            sa << '\n';
        }
    }
    return sa.take_string();
}

void
devika::add_handlers()
{
    add_read_handler("table", dump_mappings_handler);
    add_read_handler("mappings", dump_mappings_handler, 0, Handler::h_deprecated);
    add_rewriter_handlers(true);
}

CLICK_ENDDECLS
ELEMENT_REQUIRES(IPRewriterBase)
EXPORT_ELEMENT(devika)
