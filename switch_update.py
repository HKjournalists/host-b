# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: wangbin19@baidu.com
Date:    2015/07/09 01:26:24
"""

import re
import os
import sys
import time
import socket
import StringIO
import telnetlib

class TelnetXorplus(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.telobj = None

    def connect(self, timeout=30):
        '''连接交换机（xorplus系统）
        Args:
        Returns:
            0: 正常连接
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
        '''
        self.telobj = None   #telobj有可能存储了已失效的telnet连接，因此先将其清除
        try:
            tel = telnetlib.Telnet(self.ip)
            ret = tel.expect([r'login:', r'.*>'], timeout)
            if ret[0] == -1:
                tel.close()
                return -1
            elif ret[0] == 0:
                if(self.username == '' or self.password == ''):
                    tel.close()
                    return -2
                #需要转码为ascii，似乎是因为telnetlib库的编码问题
                tel.write(self.username.encode('ascii') + '\n')  
                ret = tel.expect([r'Password:'], timeout)
                if ret[0] == 0:
                    tel.write(self.password.encode('ascii') + '\n')
                    ret = tel.expect([r'.*>'], timeout)
                    if ret[0] == -1:
                        tel.close()
                        return -1
                else:
                    tel.close()
                    return -1
            tel.write('set cli idle-timeout 0\n')
            ret = tel.expect([r'.*>'], timeout)
            if ret[0] == 0:
                tel.write('configure\n')
                ret = tel.expect([r'.*#'], timeout)
                if ret[0] == 0: 
                    self.telobj = tel   
                    return 0
            tel.close()
            return common.SWITCH_LOGIN_ERR
        except EOFError as eof:
            #print eof
            self.close()   
            return -4 
        except socket.error as serr:
            #print serr
            self.close()
            return -3        

    def close(self):
        '''关闭连接
        '''
        if self.telobj is not None:
            self.telobj.close()
            self.telobj = None

    def getConn(self, timeout=30):
        '''获取连接，若链接不存在或已失效则重新连接
        Args:
        Returns:
            0: 获取到连接
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
        '''
        if self.telobj is None:
            ret = self.connect()
            if ret != 0:
                return ret
        try:
            self.telobj.write('\n')
            self.telobj.expect([r'.*#'], timeout)
            return 0
        except EOFError as eof:
            #print eof
            self.close()
            return -4

    def send_nocommit(self, cmd, explist, timeout=10):
        '''连接交换机，执行命令但不commit，用于执行不需要commit的命令，如show xxx
        Args:
            cmd: 要执行的命令
            explist: 命令的预期执行结果列表，列表元素为与预期执行结果
                     对应的正则表达式或字符串，若无法匹配列表中元素，则认为
                     执行出错。列表通常只需要包含预期的正确结果，例如：执行
                     run show vlans vlan-id 2，交换机不存在vlan 2，因此期望
                     结果为：syntax error, expecting `1'，则set_explist应传
                     入实参[r'syntax error, expecting.*']。
            timeout: 超时时间
        Returns:
            >=0: 与命令返回结果匹配的explist中元素的编号
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的set_explist，commit_explist参数不是列表类型，或cmd包含'\n'
            -6: set命令出错，一般由于命令格式有问题
        '''
        if type(explist) != list or cmd.rfind('\n') != -1:
            return -5
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            tel.write((cmd + '\n').encode('ascii'))
            ret = tel.expect(explist, timeout)
            if ret[0] == -1:
                #print ret[1] + '\n' + ret[2]
                self.close()
                return -6
            #print ret[1].group()
            self.close()
            return ret[0]
        except EOFError as eof:
            #print eof
            self.close()
            return -4

    def shell_cmd(self, cmds, timeout=300):
        '''连接交换机，进入命令行执行指令
        Args:
            cmd: 要执行的命令列表
            timeout: 超时时间
        Returns:
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
            -6: 命令结果出错（不符合预期）
        '''
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            tel.write('run start shell sh\n')
            ret = tel.expect(['Input password:'], timeout)
            #print ret[2]
            if ret[0] == -1:
                self.close()
                return -6
            tel.write('toor\n')
            ret = tel.expect(['$'], timeout)
            if ret[0] == -1:
                self.close()
                return -6
            #print ret[2]
            tel.write('su root\n')
            ret = tel.expect(['Password:'], timeout)
            if ret[0] == -1:
                self.close()
                return -6
            #print ret[2]
            tel.write('toor\n')
            ret = tel.expect(['#'], timeout)
            if ret[0] == -1:
                self.close()
                return -6
            #print ret[2]
            for cmd in cmds:
                if cmd.rfind('\n') != -1:
                    return -5
                tel.write((cmd + '\n').encode('ascii'))
                time.sleep(10)
            #msg = tel.read_very_eager()
            #print msg
            self.close()
            return 0
        except EOFError as eof:
            print eof
            self.close()
            return -4

    def update_system(self, tftphost, file):
        '''连接交换机，进行系统升级
        Args:
            tftphost: tftp服务器ip
            file: 升级文件名
        Returns:
            0: 正常执行
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的set_explist，commit_explist参数不是列表类型，或cmd包含'\n'
            -6: set命令出错，一般由于命令格式有问题
        '''
        cmd ='run file tftp get remote-file %s local-file rootfs.tar.gz ip-address %s'\
             % (file, tftphost) 
        if self.send_nocommit(cmd, ['Done!'], 300) == 0:
            print('download %s success' % (file))
        if self.shell_cmd(['reboot']) == 0:
            print('reboot success')

if __name__ == '__main__':
    
    if(len(sys.argv) != 3):
        print "help of system_update.py\n"
        print "\t参数1: 待升级交换机ip\n\t参数2: 需要下载的系统文件名\n"
    else:
        #print("ip: %s\nfile: %s\n" % (sys.argv[1], sys.argv[2]))
        t = TelnetXorplus(sys.argv[1], 'admin', 'admin')
        t.update_system('192.168.30.92', sys.argv[2])

