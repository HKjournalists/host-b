#!/bin/bash
# -*- coding: utf8 -*-

from caselib.diskinit import diskinit_template
from util import utilities

class DiskInitCase(diskinit_template.DiskInitTemplate):
    
    def __init__(self): 
        super(DiskInitCase, self).__init__('diskinit case21', 'raid0-ext2-nromal')
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
                                "file_system":"Ext2",
                                "large_fs":"normal",
                                "block_size":"4K",
                                "fs_options":["extent", "journal"]
                            },
                            "mount_point":["\/home","\/home\/disk1","\/home\/disk2","\/home\/disk3","\/home\/disk4",
                                           "\/home\/disk5"],
                            "mount_point_flash":"",
                            "flash_quantity":"",
                            "raid_level":"0",
                            "disk":[{"disk_size":"300G","disk_quantity":"6"}],
                            "keep_home":"no",
                            "serial_number":"BDSGJ21320310",
                            'hostname': 'bb-atm-ur-sandbox01.bb01'
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
        self.ip = '192.168.1.11'        
        self.projcet = 'SOC-DiskInit'
        self.version = '1.0.5'
        self.result = ''
        self.msg = ''
        self.expect_ret = {"status": "0"}        

