#!/usr/bin/env python
#-*- coding: utf-8 -*-
import socket

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 10010))
    rcvdata = '{"status": -1, "uuid": "344314", "outsource": 0, "msg": "\u64cd\u4f5c\u6210\u529f\", "error_code": 39001}&sig=CF57433B2CE32FF59B25E457B3205E4E&002217250914'
    s.send(rcvdata)
    s.close()
except socket.error, e:
    (errno, err_msg) = e 
    print "Socket error: %s, errno=%d" % (err_msg, errno)

