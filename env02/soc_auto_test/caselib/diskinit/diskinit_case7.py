#!/bin/bash
# -*- coding: utf8 -*-

from caselib.diskinit import diskinit_template
from util import utilities

class DiskInitCase(diskinit_template.DiskInitTemplate):
    
    def __init__(self): 
        super(DiskInitCase, self).__init__('diskinit case7', 'worng flash mount point')
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
                            "mount_point":["\/home"],
                            "mount_point_flash":["\/home\/ssd", "\/home\/ssd1", "\/home\/ssd2"],
                            "flash_quantity":"4",
                            "raid_level":"0",
                            "disk":[{"disk_size":"500G","disk_quantity":"2"}],
                            "keep_home":"no",
                            "serial_number":"06PZRN7",
                            'hostname': 'bb-atm-ur-sandbox02.bb01'
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
        self.ip = '192.168.1.12'        
        self.projcet = 'SOC-DiskInit'
        self.version = '1.0.5'
        self.result = ''
        self.msg = ''
        self.expect_ret = {"status": "-1"}        

