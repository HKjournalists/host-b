# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'wangbin19'

class History(object):
    
    def __init__(self, ip, username, passwd):
        self.ip = ip
        self.username = username
        self.passwd = passwd
        self.cmdlist = []

    def add(self, cmd):
        self.cmdlist.append(cmd)

