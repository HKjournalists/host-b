__author__ = 'yangguang07'
#!/usr/bin/env python
#-*- coding: utf-8 -*-
import json
from socket import *
import time
import sys
import os
import re
import hashlib
import struct
import copy


HOST = '127.0.0.1'
PORT = 8010
BUFSIZ = 1024 * 1024
ADDR = (HOST, PORT)
PRIVATEKEY = '10000'


def make_nshead(lens):
    nshead = {
        "id": 0,
        "version": 1,
        "log_id": 0,
        "provider": 'soc-agent',
        #"provider" : 'soc-axxxxgent',
        "magic_num": 0xfb709394,
        "reserved": 0,
        "body_len": lens,
    }

    header = []

    for i in ["id", "version", "log_id", "provider", "magic_num", "reserved", "body_len"]:
        header.append(nshead[i])

    header_p = struct.pack("2HI16s3I", *header)
    print "nsheader: " + header_p
    return header_p


def input(data, timestamp=None, randuuid=False):
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)

    if not data:
        return 0

    if randuuid:
        for task in data['task']:
            task['uuid'] = random.randint(100000, 999999)
    d = json.dumps(data, ensure_ascii=False)
    print "\njsond: " + d + "\n"
    m = hashlib.md5()
    if timestamp == None:
        timestamp = time.strftime("%H%M%S%d%m%y", time.localtime(time.time()))
    m.update(d + timestamp + PRIVATEKEY)
    my_sig = m.hexdigest().upper()
    u = d + "&sig=" + my_sig + '&' + timestamp
    print "u: " + u + "\n"
    #header = make_nshead(0)
    header = make_nshead(len(u))
    send_data = u
    print "sd: " + send_data + "\n"
    starttime = time.time()
    tcpCliSock.send('%s\r\n' % send_data)
    data = tcpCliSock.recv(BUFSIZ)
    file = open('/var/tmp/soc_cli.ret', "w")
    file.write(data[36:])
    file.flush()
    file.close()
    timecost = time.time() - starttime
    print "timecost:%s" % str(timecost) + "\n"
    print "sd:" + data + "\n"
    tcpCliSock.close()


if __name__ == "__main__":

    tilo = {
        "count": 1,
        "ReplyAddr": "192.168.1.14:10000",
        "task": [{
                     "json": {
                         "opname": "ILO_CHK",
                         "args": {
                             "ilo_ip": "172.16.1.11",
                             "sn": "BDSGJ21320310"
                         },
                         "attr": {
                             "country": "China",
                             "other": "",
                             "area": "HB",
                             "city": "",
                             "wh": "DB"
                         }
                     },
                     "uuid": 3924
                 }],
        "From": "RMS",
        "APIVersion": 1
    }
    tsendconfgen_yg = {
        "count": 1,
        "ReplyAddr": "192.168.1.14:10000",
        "task": [{
                     "json": {
                         "opname": "SEND_INSTALL_PARAMS",
                         "args": {
                             "sa": "yangguang07@baidu.com",
                             "secondary_ip_netmask": "",
                             "serial_number": "YGYGWAN521",
                             "secondary_ip": "",
                             "root_partition_location": "/dev/sda2",
                             "raid_rw_ratio": "",
                             "root_partition_area_size": 4096,
                             "swap": "off",
                             "ssd": [{"ssd_quantity": "6", "ssd_size": "480G"}],
                             "root_partition_size": "20G",
                             "keep_home": "yes",
                             "template_id": "5",
                             "type": "fast_online",
                             "swap_partition": "",
                             "raid_level": "1",
                             "outer_ip": "",
                             "ilo_ip": "3.3.3.3",
                             "main_in_ip_netmask": "255.255.255.0",
                             "main_in_ip": "10.42.168.15",
                             "idc": "M1",
                             "hostname": "m1-sys-ra-banqianssd2276.m1",
                             "is_install_pkgname": "centos6u3",
                             "os": "linux",
                             #"kernel_version": "",
                             "kernel_version": "2.6.32_1-13-0-0",
                             "firmware": [],
                             "model": "X3550M4",
                             "NCSI": "0",
                             "memory": [{"mem_size": "8G", "mem_quantity": "6"}],
                             "bios": [],
                             "disk": [{"disk_size": "500G", "disk_quantity": "2"}]
                         },
                         "attr": {
                             "country": "China",
                             "other": "",
                             "area": "HB",
                             "city": "",
                             "wh": "DB"
                         }
                     },
                     "uuid": 3924
                 }],
        "From": "RMS",
        "APIVersion": 1
    }
    tai_yg = {
        "count": 1,
        "ReplyAddr": "192.168.1.14:10000",
        "task": [{
                     "json": {
                         "opname": "AUTO_INSTALL",
                         "args": {
                             "hostname": "m1-sys-ra-banqianssd2276.m1",
                             "idc": "M1",
                             "ilo_ip": "10.42.168.15",
                             "model": "X3550M4",
                             "sn": "06PZRH2"
                         },
                         "attr": {
                             "country": "China",
                             "other": "",
                             "area": "HB",
                             "city": "",
                             "wh": "DB"
                         }
                     },
                     "uuid": 3924
                 }],
        "From": "RMS",
        "APIVersion": 1
    }

    tsendconfgen = {
        "count": 1,
        "ReplyAddr": "192.168.1.14:10000",
        "task": [{
                     "json": {
                         "opname": "SEND_INSTALL_PARAMS",
                         "args": {
			     "is_host_machine":0,
                             "is_install_pkgname": "centos6u3",
                             "os": "linux",
                             "producer":"IBM",
                             "kernel_version": "2.6.32_1-13-0-0",
                             "raid_rw_ratio": "50:50",
                             "keep_home": "no",
                             "template_id": "5",
                             "raid_level": "5",
                             "sa": "yangguang07@baidu.com",
                             "secondary_ip_netmask": "",
                             "serial_number": "BDSGJ21320311",
                             "secondary_ip": "",
                             "root_partition_location": "/dev/sda2",
                             "root_partition_area_size": 4096,
                             "swap": "off",
                             "ssd": [],
                             "root_partition_size": "20G",
                             "type": "self_reinstall",
                             "swap_partition": "",
                             "outer_ip": "",
                             "ilo_ip": "172.16.1.13",
                             "main_in_ip_netmask": "255.255.255.0",
                             "main_in_ip": "192.168.1.13",
                             "idc": "BB",
                             "hostname": "bb-atm-ur-sandbox03.bb01",
                             "firmware": [],
                             "model": "I610-G10",
                             "NCSI": "0",
                             "memory": [{"mem_size": "8G", "mem_quantity": "8"}],
                             "bios": [],
                             "disk": [{"disk_size": "300G", "disk_quantity": "6"}]
                         },
                         "attr": {
                             "country": "China",
                             "other": "",
                             "area": "HB",
                             "city": "",
                             "wh": "DB"
                         }
                     },
                     "uuid": 3524
                 }],
        "From": "RMS",
        "APIVersion": 1
    }
    tsoftreinstall = { 
        "count": 1,
        "From": "RMS",
        "APIVersion": "1",
        "ReplyAddr": "192.168.1.14:10000",
        "task": [
            {   
                "uuid": "3299",
                "json": {
                    "opname": "SOFT_REINSTALL",
                    "args": {
                        "sn": "BDSGJ21320311",
                        "hostname": "bb-atm-ur-sandbox03.bb01",
                        "model": "I610-G10",
                        "iloip": "172.16.1.13"
                    },  
                    "attr": {
                        "country": "country",
                        "area": "area",
                        "city": "city",
                        "wh": "wh",
                        "other": "other"
                    }   
                }   
            }   
             ]   
    }
    tfinalcheck = copy.deepcopy(tsendconfgen)
    tfinalcheck['task'][0]['json']['opname']='FINISH_CHK'
    #print id(tsendconfgen),id(tfinalcheck)
    tdiskinit = {
        "count": 1,
        "From": "RMS",
        "APIVersion": "1",
        "ReplyAddr": "192.168.1.14:10000",
        "task": [
            {
                "uuid": "6294",
                "json": {
                    "opname": "DISK_INIT",
                    "args" :
                    {
                        "format_file_system":
                        {
                            "id":"name2",
                            "file_system":"Ext4",
                            #"large_fs":"normal",
                            "large_fs":"largefile",
                            "block_size":"4K",
                            "fs_options":["journal","extent"]
                            #"fs_options":[]
                        },
                        "mount_point":["\/home"],
                        #"mount_point":["\/home","\/home\/disk1","\/home\/disk2","\/home\/disk3","\/home\/disk4","\/home\/disk5","\/home\/disk6","\/home\/disk7","\/home\/disk8","\/home\/disk9"],
                        #"mount_point_flash":["\/home\/ssd1","\/home\/ssd2","\/home\/ssd3","\/home\/ssd4"],
                        "mount_point_flash":[],
                        "flash_quantity":"4",
                        "raid_level":"0",
                        "disk":[{"disk_size":"300G","disk_quantity":"6"}],
                        "keep_home":"no",
                        "serial_number":"",
                        'hostname': 'bb-atm-ur-sandbox03.bb01'
                    },
                    "attr": {
                        "country": "country",
                        "area": "area",
                        "city": "city",
                        "wh": "wh",
                        "other": "other"
                    }
                }
            }
        ]
    }
    tflashinit = {
        "count": 1,
        "From": "RMS",
        "APIVersion": "1",
        "ReplyAddr": "192.168.1.14:10000",
        "task": [
            {
                "uuid": "6294",
                "json": {
                    "opname": "FLASH_INIT",
                    "args" :{
		        "raid": [
			    #{"raid_stripesize": "128","raid_level": "0","raid_rw_ratio": "50:50"},
			    #{"raid_stripesize": "128","raid_level": "0","raid_rw_ratio": "50:50"},
			    #{"raid_stripesize": "128","raid_level": "0","raid_rw_ratio": "50:50"},
			    #{"raid_stripesize": "128","raid_level": "0","raid_rw_ratio": "50:50"},
			    {"raid_stripesize": "128","raid_level": "0","raid_rw_ratio": "50:50"}
			],
		        "flash_type": "ssd",
	       	        "hostname": "bb-atm-ur-sandbox02.bb01",
		        "flash_new_raid": "1",
	    	        "flash_one_raid": "1",
			"flash_quantity": "4",
			"sn": "06PZRN7",
			"flash_size": "480G",
			"flash_logic": "010"
		    },
                    "attr": {
                        "country": "country",
                        "area": "area",
                        "city": "city",
                        "wh": "wh",
                        "other": "other"
                    }
                }
            }
        ]
    }
    tai = {
        "count": 1,
        "ReplyAddr": "192.168.1.14:10000",
        "task": [{
                     "json": {
                         "opname": "AUTO_INSTALL",
                         "args": {
                             "hostname": "bb-atm-ur-sandbox06.bb01",
                             "idc": "BB",
                             "ilo_ip": "172.16.1.16",
                             "model": "X3630",
                             "sn": "06PPXK1"
                         },
                         "attr": {
                             "country": "China",
                             "other": "",
                             "area": "HB",
                             "city": "",
                             "wh": "DB"
                         }
                     },
                     "uuid": 3924
                 }],
        "From": "RMS",
        "APIVersion": 1
    }
	
    import random
    #input(tilo, timestamp = None, randuuid = True)
    #input(tsendconfgen, timestamp=None, randuuid=True)
    #time.sleep(10)
    input(tsoftreinstall, timestamp=None, randuuid=True)
    #input(tai, timestamp=None, randuuid=True)
    #input(tfinalcheck, timestamp=None, randuuid=True)
    #input(tdiskinit, timestamp=None, randuuid=True)
    #input(tflashinit, timestamp=None, randuuid=True)

    

