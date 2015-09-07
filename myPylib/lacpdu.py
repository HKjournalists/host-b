#! /usr/bin/evn python

################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide lacp frame struct with python.

Authors: wuxiaoying(wuxiaoying01@baidu.com)
Date:    2015/06/23 13:00:06
"""

from scapy.packet import Packet
from scapy.packet import bind_layers
from scapy.fields import ByteField
from scapy.fields import ShortField
from scapy.fields import MACField
from scapy.fields import FlagsField
from scapy.fields import StrFixedLenField
from scapy.layers.l2 import Ether
from scapy.config import conf
from scapy.data import ETHER_ANY

class LACP(Packet):
    """lacp frame struct.

    every filed in the lacpdu
    
    Attributes:
        name: the name of the frame.
        fields_desc: every filed in a lacpdu.
    """
    name = "Lacp"
    fields_desc = [ByteField("SubType", 1),
                    ByteField("Version number", 1),
                    ByteField("Actor_Information", 1),
                    ByteField("Actor_Information_Length", 0x14),
                    ShortField("Actor_system_priority", 1),
                    MACField("Actor_system", ETHER_ANY),
                    ShortField("Actor_key", 0),
                    ShortField("Actor_port_priority", 0),
                    ShortField("Actor_port", 0),
                    FlagsField("Actor_state", 0, 8, ["LACP_Activity", \
                    "LACP_Timeout", "Aggregation", \
                    "Synchronization", "Collecting", \
                    "Distributing", "Defaulted", "Expired"]),
                    StrFixedLenField("reserve", "\x00" * 3, 3),
                    ByteField("Partner_Information", 2),
                    ByteField("Partner_Information_Length", 0x14),
                    ShortField("Partner_system_priority", 0),
                    MACField("Partner_system", ETHER_ANY),
                    ShortField("Partner_key", 0),
                    ShortField("Partner_port_priority", 0),
                    ShortField("Partner_port", 0),
                    FlagsField("Partner_state", 0, 8, ["LACP_Activity", \
                    "LACP_Timeout", \
                    "Aggregation", \
                    "Synchronization", \
                    "Collecting", \
                    "Distributing", \
                    "Defaulted", \
                    "Expired"]),
                    StrFixedLenField("reserve", "\x00" * 3, 3),
                    ByteField("Collector_Information", 3),
                    ByteField("Collector_Information_Length", 0x10),
                    ShortField("CollectorMaxDelay", 0),
                    StrFixedLenField("reserve", "\x00" * 12, 12),
                    ByteField("Terminator_Information", 0),
                    ByteField("Terminator_Information_Length", 0x10),
                    StrFixedLenField("reserve", "\x00" * 50, 50)]
conf.neighbor.register_l3(Ether, LACP, lambda l2, l3: conf.neighbor.resolve(l2, l3.payload))
bind_layers(Ether, LACP, type = 34825)

