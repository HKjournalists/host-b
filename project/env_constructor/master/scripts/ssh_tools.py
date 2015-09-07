#!/usr/bin/env python
# -*- coding: utf8 -*-

import paramiko
import socket
import StringIO

class SshConnect(object):
    
    def __init__(self, host, user, passwd, timeout = 30, verbose = False):
        '''构造方法
        Args:
            host: 主机ip
            user: 用户名
            passwd: 密码
            timeout: 超时时间
            verbose: 是否显示详情
        Returns:
            无
        '''
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
        '''建立ssh连接
        Args:
            无
        Returns:
            0: 正常
            -10: 认证失败，可能由于用户民/密码错误
            -11: 连接失败
        '''
        try:
            if self.transport and self.transport.is_authenticated(): 
                return 0
            if not self.transport:
                self.transport = paramiko.Transport((self.host, 22))
            if not self.transport.is_alive():
                self.transport.connect(username=self.username, password=self.password)
        except paramiko.AuthenticationException, e:
            print 'Authentication failed, please chech user name and passwrod!'
            return -10
        except paramiko.SSHException, e:
            print e
            return -11  #连接出现异常
        return 0

    def open_session(self):
        '''建立ssh会话
        Args:
            无
        Returns:
            channel: 建立完成的ssh会话
            -10: 认证失败，可能由于用户民/密码错误
            -11: 连接失败
            -21: 尝试访问未知的对象属性
            -22: ssh连接已经关闭
        '''
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
        '''通过ssh会话发送远程指令
        Args:
            cmd: 需要发送的指令
            timeout: 超时时间
        Returns:
            recv_exit_status: 指令执行后的退出状态
            -10: 认证失败，可能由于用户民/密码错误
            -11: 连接失败
            -21: 尝试访问未知的对象属性
            -22: ssh连接已经关闭
            -31: 连接超时
        '''
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
        '''通过sftp由本地向ssh主机传输文件
        Args:
            src: 本地文件路径
            dst: 远程目标路径
            timeout: 超时时间
        Returns:
            0: 正常
            -10: 认证失败，可能由于用户民/密码错误
            -11: 连接失败
        '''
        ret = self.connect()
        if(ret != 0):
            return ret
        self.sftpObj = self.transport.open_sftp_client()
        if timeout:
             self.sftp.get_channel().settimeout(timeout)
        self.sftpObj.put(src, dst)
        return 0

    def get_cmd_ret(self, cmd, timeout = None):
        '''执行远程命令并获取输出信息（主要用于读取远程主机信息）
        Args:
            cmd: 需要执行的命令
            timeout: 超时时间
        Returns:
            lines: 获取的信息（字符串列表形式）
            -10: 认证失败，可能由于用户民/密码错误
            -11: 连接失败
            -21: 尝试访问未知的对象属性
            -22: ssh连接已经关闭
            -31: 连接超时
        '''
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
    list = s.get_cmd_ret('ip r')
    for l in list:
        l = l.split()
        if 'via' in l:
            continue
        print l




        
