#!/usr/bin/env python
# -*- coding: utf8 -*-

import paramiko
import socket
import StringIO

class SshConnect(object):
    
    def __init__(self, host, user, passwd, timeout = 30, verbose = False):
        self.transport = None
        self.sftpObj = None
        self.host = host
        self.username = user
        self.password = passwd
        self.timeout = timeout
        self.verbose = verbose
        
    def settimeout(self, t):
        self.timeout = t

    def connect(self):
        try:
            if self.transport and self.transport.is_authenticated(): 
                return 0
            if not self.transport:
                self.transport = paramiko.Transport((self.host, 22))
            if not self.transport.is_alive():
                self.transport.connect(username = self.username, password = self.password)
        except paramiko.SSHException, e:
            print e
            return -1  #连接出现异常，可能由连接超时或认证失败引起
        return 0

    def open_session(self):
        ret = self.connect()
        if(ret != 0):
            return ret
        try:
            channel = self.transport.open_channel('session')
        except AttributeError:
            return -21
        except EOFError:
            return -22
        return channel
    
    def send_cmd(self, cmd, timeout = None):
        channel = self.open_session()
        if type(channel) == int:
            return channel 
        if timeout:
            channel.settimeout(timeout)
        else:
            channel.settimeout(self.timeout)
        channel.set_combine_stderr(True)
        #print cmd 
        channel.exec_command(cmd)
        try:
            tmp = ' '         # set tmp init to ' ', prevent it to be None
            data = ''
            while True:
                tmp = channel.recv(10240)
                if self.verbose:
                    print tmp
                if tmp == '':   # if tmp is None, channel is close
                    break
                data = tmp    # capure only the last 10240 bytes
            if data:
                data = data.strip()
            #print data
        except socket.timeout:
            return -31
        return str(channel.recv_exit_status())
    
    def sftp(self, src, dst, timeout = None):
        self.connect()
        self.sftpObj = self.transport.open_sftp_client()
        if timeout:
             self.sftp.get_channel().settimeout(timeout)
        self.sftpObj.put(src, dst)

    def get_cmd_ret(self, cmd, timeout = None):
        channel = self.open_session()
        if type(channel) == int:
            return channel 
        if timeout:
            channel.settimeout(timeout)
        else:
            channel.settimeout(self.timeout)
        channel.set_combine_stderr(True)
        channel.exec_command(cmd)
        try:
            tmp = ' '         # set tmp init to ' ', prevent it to be empty
            data = ''
            while True:
                tmp = channel.recv(10240)
                if tmp == '':   # if tmp is empty, channel is close
                    break
                data = tmp    # capure only the last 10240 bytes
            if data is not None:
                data = data.strip()
            buffer = StringIO.StringIO(data)
            lines = buffer.readlines()
            buffer.close()
            return lines
        except socket.timeout:
            return -31
        return str(channel.recv_exit_status())

        
    def __del__(self):
        #print 'finalize'
        if self.sftpObj:
            self.sftpObj.close()
        if self.transport:
            self.transport.close()

if __name__ == '__main__':
    s = SshConnect('10.32.15.34', 'root', 'sysqa@ftqa')    
    #s.send_cmd('rm -f /tmp/aaaasssss')
    #s.send_cmd('touch /tmp/aaaa1sssss')
    #s.sftp('log', '/tmp/log')
    print s.get_cmd_ret('ip a')





        
