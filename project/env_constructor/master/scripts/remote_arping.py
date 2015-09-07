# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
import sys
import socket
from scapy.all import srp, arping
from scapy.layers.l2 import Ether, ARP

def remote_arping(sip, dev, dip):
    ans = None
    unans = None
    try:
        ans, unans = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(psrc=sip, pdst=dip), verbose=0,
                         filter='arp and arp[7] = 2', iface=dev, timeout=2)
    except socket.error, e:
        (etype, evalue, etrace) = sys.exc_info()
        (errno, err_msg) = evalue
        if errno == 19:
            print('-1')
            return -1
    if ans is not None and len(ans) == 1:
        (s, r) = ans[0]
        if r.payload.psrc == dip:
            print('1')
            return 1
    print('0')
    return 0

sip = sys.argv[1] 
dev = sys.argv[2] 
dip = sys.argv[3]
remote_arping(sip, dev, dip)