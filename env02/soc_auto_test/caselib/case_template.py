author__ = 'wangbin19'
# -*- coding: utf-8 -*-

import json
from socket import *
import time
import random
import sys 
import os
import hashlib
import struct

from util import utilities

HOST = '127.0.0.1'
PORT = 8010
BUFSIZ = 1024 * 1024
ADDR = (HOST, PORT)
PRIVATEKEY = '20000'

class CaseTemplate(object):
	
    def __init__(self, name = 'case template' , description = 'base class of all cases'):
        self.name = name
        self.description = description
        self.expect_ret = {"status": "0"}
        self.expect_status_code = 0
        self.expect_redis = {}
        self.expect_mysql = {}
        self.input_name = __file__
        self.input_dest = ''		
        self.input_action = ''
        self.input_data = {}
        self.setup_have_pxe_task = False
        self.setup_clean_redis = False
        self.setup_redis_cmds = []
        self.setup_mysql_cmds = []
        self.teardown_redis_cmds = []
        self.teardown_mysql_cmds = []
        self.uuid = 0
        self.utilObj = utilities.AutoTestUtil()

    def make_nshead(self, lens):
        nshead = {
            "id": 0,
            "version": 1,
            "log_id": 0,
            "provider": 'soc-agent',
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
    
    def pre(self):
        if self.setup_clean_redis == True:
            #print 'clean redis!'
            self.utilObj.clredis()
        #else:
            #print 'skip clean redis!'

    def doTest(self, randid = True, timestamp = None):
        if not self.input_data:
            print 'no data'
            return
        tcpConnect = socket(AF_INET, SOCK_STREAM)
        tcpConnect.connect(ADDR)
        if randid:
            for task in self.input_data['task']:
                self.uuid = task['uuid'] = random.randint(100000, 999999)
        d = json.dumps(self.input_data, ensure_ascii=False)
        print "\njson data: " + d + "\n"
        if timestamp == None:
            timestamp = time.strftime("%H%M%S%d%m%y", time.localtime(time.time()))
        m = hashlib.md5()
        m.update(d + timestamp + PRIVATEKEY)
        my_sig = m.hexdigest().upper()
        u = d + "&sig=" + my_sig + '&' + timestamp
        print "data with sig: " + u + "\n"
        #header = self.make_nshead(len(u))
        send_data = u
        print "send data: " + send_data + "\n"
        starttime = time.time()
        tcpConnect.send('%s\r\n' % send_data)
        data = tcpConnect.recv(BUFSIZ)
        file = open('/home/wangbin/autotest/returnlog', "w")
        file.write(data[36:])
        file.flush()
        file.close()
        timecost = time.time() - starttime
        #print "timecost:%s" % str(timecost) + "\n"
        #print "sd:" + data + "\n"	
        tcpConnect.close()

    def verify(self):
        #print 'wait for verify'
        data = self.utilObj.atserver(self.uuid)
        if not data:
            print 'no data'
            return 0
        #print type(data)
        if data['status'] == int(self.expect_ret['status']): 
            self.result = 'success'
            #print 'case success!\nmsg: %s' % (data['msg'])
        else: 
            self.result = 'faild'
            #print 'case faild!\nerror code: %d\nerror msg: %s' % (data['error_code'], data['msg'])
        self.msg = data['msg']


if __name__ == '__main__':
    print ''

















		





