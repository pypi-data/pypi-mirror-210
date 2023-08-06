#ifdef NS3_MODULE_COMPILATION 
    error "Do not include ns3 module aggregator headers from other modules these are meant only for end user scripts." 
#endif 
#ifndef NS3_MODULE_OPENFLOW
    // Module headers: 
    #include <ns3/openflow-switch-helper.h>
    #include <ns3/openflow-interface.h>
    #include <ns3/openflow-switch-net-device.h>
#endif 