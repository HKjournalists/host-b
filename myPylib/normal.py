#! /usr/bin/evn python

################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module test lacpdu successful switch process .

Authors: wuxiaoying(wuxiaoying01@baidu.com)
Date:    2015/06/23 13:00:06
"""

from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp
from scapy.sendrecv import srp
from scapy.error import Scapy_Exception
import sys
sys.path.append("/home/wuxiaoying/lacp/lacpconference")
from lacpdu import LACP

def verify():
    """

    Retrieves rows pertaining to the given keys from the Table instance
    represented by big_table.  Silly things may happen if
    other_silly_variable is not None.

    Args: None
    Returns:
        if first lacpdu switch pass, receive lacpdu.actor.syn=true
            print pass1
            if the second lacpdu switch pass,receive lacp.actor.state=0x3d
                print PASS2
                return 2
        else not a successful switch process
            return 3 
    Raises:
        Scapy_Exception: An error occurred accessing scapy.
    """
    a=Ether(dst='01:80:c2:00:00:02', src='00:1B:21:6A:C2:6F', type=0x8809)/LACP(\
        Actor_system='00:1B:21:6A:C2:6F', \
        Actor_key=1, \
        Actor_port_priority=1, \
        Actor_port=1, \
        Actor_state=0x45, \
        Partner_system='00:00:00:00:00:00', \
        Partner_state=0x02, CollectorMaxDelay=5000)
    sendp(a, iface='xgbe0', count=1)
    #send a LACPDU with actor information and without partner information,then recv a LACPDU reply show switch syn
    ans, unans=srp(a, iface='xgbe0', timeout=60)
    for s, r in ans:
        if r.haslayer(LACP):
            r.show()
            partner_system_priority=r.sprintf('%LACP.Actor_system_priority%')
            partner_system=r.sprintf('%LACP.Actor_system%')
            partner_key=r.sprintf('%LACP.Actor_key%')
            partner_port_priority=r.sprintf('%LACP.Actor_port_priority%')
            partner_port=r.sprintf('%LACP.Actor_port%')
            partner_state_lacpdu=r.sprintf('%LACP.Actor_state%')
            if partner_state_lacpdu == 'LACP_Activity+Aggregation+Synchronization':
                print "PASS1"
                b=Ether(dst='01:80:c2:00:00:02', src='00:1B:21:6A:C2:6F', type=0x8809)/LACP(\
                        Actor_system='00:1B:21:6A:C2:6F', \
                        Actor_key=1, \
                        Actor_port_priority=1, \
                        Actor_port=1, Actor_state=0x0d, \
                        Partner_system=partner_system, \
                        Partner_system_priority=int(partner_system_priority), \
                        Partner_key=int(partner_key), \
                        Partner_port_priority=int(partner_port_priority), \
                        Partner_port=int(partner_port), \
                        Partner_state=0x0d, CollectorMaxDelay=5000)
                ans1, unans1=srp(b, iface='xgbe0')
                for s1, r1 in ans1:
                    if r1.haslayer(LACP):
                        r1.show() 
                        partner_state1_lacpdu=r1.sprintf('%LACP.Actor_state%')
                        print type(partner_state1_lacpdu)
                        if partner_state1_lacpdu == 'LACP_Activity\
        +Aggregation+Synchronization+Collecting+Distributing':
                            print "PASS2"
                            exit(2)
                        else:
                            print "switch is not lacpactive"
                            exit(3)
                    else:
                        print "recv is not LACPDU"
                        exit(3)
            else:
                print "switch is not Synchronization"
                exit(3)

        else:
            exit(3)
if __name__ == "__main__":
    try:
        verify()
    except Scapy_Exception:
        print 'exception happened!!'

