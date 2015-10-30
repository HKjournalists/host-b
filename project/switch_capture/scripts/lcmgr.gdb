directory /pica/bin/lcmgr/debug_src_dir
symbol-file /pica/bin/lcmgr/pica_lcmgr.debug
b rx_packet_callback
b XrlLcmgrNode::read_rx_event_callback
