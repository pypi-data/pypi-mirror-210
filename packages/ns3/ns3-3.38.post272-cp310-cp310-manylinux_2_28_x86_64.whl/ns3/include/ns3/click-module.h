#ifdef NS3_MODULE_COMPILATION 
    error "Do not include ns3 module aggregator headers from other modules these are meant only for end user scripts." 
#endif 
#ifndef NS3_MODULE_CLICK
    // Module headers: 
    #include <ns3/click-internet-stack-helper.h>
    #include <ns3/ipv4-click-routing.h>
    #include <ns3/ipv4-l3-click-protocol.h>
#endif 