uthor__ = 'wangbin19'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import sys
import os
import paramiko

from util import constants 
import ssh_tools

BUFSIZ = 1024 * 1024

class AutoTestUtil(object): 
    
    def atserver(self, uuid):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 10010))
        s.listen(10)
        data = None
        try:
            while True:
                con, addr = s.accept()
                data = con.recv(BUFSIZ)
                data = eval(data.split('&')[0])
                if(int(data['uuid']) == self.uuid):
                    con.close()
                    break
                else:
                    data = None
                con.close()
        except socket.error, e:
            (errno, err_msg) = e
            print "Socket error: %s, errno=%d" % (err_msg, errno)
        except KeyboardInterrupt:
            print 'Interrupt by ctrl + C'
        except EOFError:
            print 'Interrupt by EOF'
        finally:
            s.close()    
            return data
        
    def clredis(self):
        try:
            
            login_redis = 'redis-cli -h %s -p %s -a %s ' %(constants.REDIS_ADDR, constants.REDIS_PORT, constants.REDIS_PASSWD)
            print 'socapi'
            os.system(login_redis + 'keys socapi:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'ReqMeta'
            os.system(login_redis + 'keys ReqMeta:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'TaskSet'
            os.system(login_redis + 'keys TaskSet:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'Task'
            os.system(login_redis + 'keys Task:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'Q'
            os.system(login_redis + 'keys Q:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'TimeOut'
            os.system(login_redis + 'keys TimeOut:* | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'ExtId2IntId'
            os.system(login_redis + 'keys ExtId2IntId | ' + 'xargs ' + login_redis + 'del > /dev/null')
            print 'PxeIdMap'
            os.system(login_redis + 'keys PxeIdMap | ' + 'xargs ' + login_redis + 'del > /dev/null')
        except Exception, e: 
           pass
        return 0
    
    def ssh_cmd():
        pass





