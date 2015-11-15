directory /pica/bin/lcmgr/debug_src_dir
symbol-file /pica/bin/lcmgr/pica_lcmgr.debug
b rx_packet_callback
b XrlLcmgrTarget::lcmgr_0_1_send_packet_from_cpu
