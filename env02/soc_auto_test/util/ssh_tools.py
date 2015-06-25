#!/usr/bin/env python
# -*- coding: utf8 -*-

import paramiko
import socket

class SshConnect(object):
    
    def __init__(self, host, user, passwd, timeout = 30, verbose = False):
        self.transport = None
        self.sftpObj = None
        self.host = host
        self.username = user
        self.password = passwd
        self.timeout = timeout
        self.verbose = verbose
        
    def setTimeOut(self, t):
        self.timeout = t

    def connect(self):
        try:
            if self.transport and self.transport.is_authenticated(): 
                return
            if not self.transport:
                self.transport = paramiko.Transport((self.host, 22))
            if not self.transport.is_alive():
                self.transport.connect(username = self.username, password = self.password)
        except paramiko.SSHException, e:
            print e
    
    def sendCmd(self, cmd, timeout = None):
        self.connect()
        channel = self.transport.open_channel('session')
        if timeout:
            channel.settimeout(timeout)
        else:
            channel.settimeout(self.timeout)
        channel.set_combine_stderr(True)
        #print cmd 
        channel.exec_command(cmd)
        try:
            #if ret_code:
            #    return str(channel.recv_exit_status())
            # set tmp init to ' ', prevent it to be None
            tmp = ' '
            data = ''
            while True:
                tmp = channel.recv(10240)
                if self.verbose:
                    print tmp
                if not tmp:
                    # if tmp is None, channel is close
                    break
                # capure only the last 10240 bytes
                data = tmp
            if data:
                data = data.strip()
            #print data
        except socket.timeout:
            raise MysshException('Exec Command Timeout: %s' % cmd)
        return str(channel.recv_exit_status())
    
    def sftp(self, src, dst, timeout = None):
        self.connect()
        self.sftpObj = self.transport.open_sftp_client()
        if timeout:
             self.sftp.get_channel().settimeout(timeout)
        self.sftpObj.put(src, dst)
        
    def __del__(self):
        #print 'finalize'
        if self.sftpObj:
            self.sftpObj.close()
        if self.transport:
            self.transport.close()

if __name__ == '__main__':
    s = SshConnect('192.168.1.15', 'root', 'SYSserverpasswd1999@baidu.com')    
    #s.sendCmd('rm -f /tmp/aaaasssss')
    #s.sendCmd('touch /tmp/aaaasssss')
    s.sftp('/home/wangbin/autotest/scripts/diskinit_pre.sh', '/tmp')





        
