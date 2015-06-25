#!/usr/bin/env python
# -*- coding: utf8 -*-

import pexpect

#c = pexpect.spawn('ssh root@192.168.1.15')
#i = c.expect(['password:', pexpect.EOF, pexpect.TIMEOUT])
#print c.before
#print c.after
c = pexpect.spawn('cp a b')
i = c.expect(['`b\'?', pexpect.EOF, pexpect.TIMEOUT])
print i
print c.before
print c.match
