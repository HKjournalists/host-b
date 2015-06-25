#!/usr/bin/env python
# -*- coding: utf8 -*-

import pexpect

class firstClass(object):
	def hello(self):
		print 'name = %s\npassword = %d' % (self.name,self.password)

	def __init__(self):
		print 'this is firstClass.__init__()'
		self.name = 'wangbin'
		self.password = 123456

if __name__ == '__main__':
    c = pexpect.spawn('cp a b')
    index = c.expect(['cp: .*\?', pexpect.EOF])
    print index
