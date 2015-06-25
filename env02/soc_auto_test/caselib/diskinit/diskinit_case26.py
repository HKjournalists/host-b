#!/bin/bash
# -*- coding: utf8 -*-

from caselib.diskinit import diskinit_template
from util import utilities

class DiskInitCase1(diskinit_template.DiskInitTemplate):
    
    def __init__(self): 
        super(DiskInitCase1, self).__init__('diskinit case26', 'no hostname')
        self.input_data = {
            "count": 1,
            "From": "RMS",
            "APIVersion": "1",
            "ReplyAddr": "192.168.1.14:10000",
            "task": [{
                    "uuid": "6294",
                    "json": {
                        "opname": "DISK_INIT",
                        "args" :
                        {   
                            "format_file_system":
                            {
                                "id":"name1",
                                "file_system":"Ext4",
                                "large_fs":"largefile",
                                "block_size":"4K",
                                "fs_options":["journal","extent"]
                            },
                            "mount_point_flash":"",
                            "flash_quantity":"",
                            "mount_point":["\/home","\/home\/disk1","\/home\/disk2","\/home\/disk3","\/home\/disk4",
                                           "\/home\/disk5","\/home\/disk6","\/home\/disk7","\/home\/disk8",
                                           "\/home\/disk9","\/home\/disk10","\/home\/disk11"],
                            "raid_level":"0",
                            "disk":[{"disk_size":"3T","disk_quantity":"12"}],
                            "keep_home":"no",
                            "serial_number":"06PPXG0",
                            'hostname': ''
                        },
                        "attr": {
                            "country": "country",
                            "area": "area",
                            "city": "city",
                            "wh": "wh",
                            "other": "other"
                        }
                    }
                }]
        }
        self.ip = '192.168.1.15'        
        self.projcet = 'SOC-DiskInit'
        self.version = '1.0.5'
        self.result = ''
        self.msg = ''
        self.expect_ret = {"status": "-1"} 

