#!/usr/bin/env python

import re
import sys
import time
import errno
import socket
import struct
import traceback
import simplejson
from os.path import dirname, abspath, join
reload(sys)
sys.setdefaultencoding("utf-8")
PWD = dirname(abspath(__file__))
sys.path.append(dirname(PWD))

from nshead import *
#from util.log import *

FILE = "route_ospf_mask_30_excluded.log"
    

def recv_all(sk, total):
    data = ""
    length = total
    while length > 0:
        data += sk.recv(length)
        length = total - len(data)
    return data

def send_alarm(sk):
    rfile = open(FILE,'r')
    port_channel_list = []
    for line in rfile:
        items = re.split('\t', line)
        port_channel = items[-1].rstrip('\n')
	if port_channel not in port_channel_list:
            port_channel_list.append(port_channel)


    print port_channel_list
    alarm_type = 28
    alarm_subtype = 0
    status = int(sys.argv[2])
    #source = "nmg01-sys-netadmin00.nmg01"
    source = sys.argv[3]
    key = "rt_"+sys.argv[1]
    now = int(time.time())
    alarm_count = 1
    desc = ""
    desc_json = ""
    if status == 1:
        desc = "Route table error, port channel list:" + ','.join(port_channel_list)
        desc_json = "The ecmp routes about " + '+'.join(port_channel_list) + " are lost in hardware,fix it at now."
    elif status == 2:
        desc = "Route table recovery, port channel list:" + ','.join(port_channel_list)
        desc_json = "The ecmp routes about " + '+'.join(port_channel_list) + " are recovery by autofix."

    dict = {}
    dict['mip'] = sys.argv[1]
    dict['if_list'] = []

    if (0 != cmp(source,"qd01-sys-netadmin00.qd01")):
        if 'ae1' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae1','if_name':['te-1/1/33','te-1/1/34','te-1/1/35']})
        if 'ae2' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae2','if_name':['te-1/1/37','te-1/1/38','te-1/1/39']})
        if 'ae3' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae3','if_name':['te-1/1/41','te-1/1/42','te-1/1/43']})
        if 'ae4' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae4','if_name':['te-1/1/45','te-1/1/46','te-1/1/47']})
    else:
        if 'ae1' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae1','if_name':['te-1/1/33','te-1/1/34']})
        if 'ae2' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae2','if_name':['te-1/1/35','te-1/1/36']})
        if 'ae3' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae3','if_name':['te-1/1/37','te-1/1/38']})
        if 'ae4' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae4','if_name':['te-1/1/39','te-1/1/40']})
        if 'ae5' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae5','if_name':['te-1/1/41','te-1/1/42']})
        if 'ae6' in port_channel_list:
            dict['if_list'].append({'channel_name':'ae6','if_name':['te-1/1/43','te-1/1/44']})
		
    alarm = {
        'type':alarm_type, 
        'subtype':alarm_subtype,
        'status':status, 
        'source':source,
        'key':key,
        'time':now,
        'alarm_count':alarm_count,
        'desc':desc,
        'desc_json':dict
    }
    alarm_json = simplejson.dumps(alarm)
    nshead = make_nshead(len(alarm_json))
    sk.sendall(nshead + alarm_json)
    
def explain_response(sk):
    head = recv_all(sk, 36)
    head = parse_nshead(head)
    res = recv_all(sk, head[-1])
    print res


#ADDR = ('127.0.0.1', 33933)
ADDR = ('10.50.15.246', 27003)
sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sk.connect(ADDR)
send_alarm(sk)
#explain_response(sk)



