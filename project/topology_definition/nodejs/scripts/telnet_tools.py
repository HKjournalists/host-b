# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'wangbin19'

import re
import os
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
        Args:f
            
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

    def send_commit(self, cmd, set_explist, commit_explist, timeout=10):
        '''连接交换机，执行命令并commit，用于执行需要commit的命令（set命令为主）
        Args:
            cmd: 要执行的命令
            set_explist: set命令的预期执行结果列表，列表元素为与预期执行结果
                         对应的正则表达式或字符串，若无法匹配列表中元素，则认为
                         执行出错。列表通常只需要包含预期的正确结果，例如：执行
                         set vlans vlan-id 2，期望结果为：[edit]，则set_explist
                         应传入实参[r'\[edit\]']。
            commit_explist: commit命令的预期执行结果列表，使用方式同set_explist
            timeout: 超时时间
        Returns:
            >=0: 与命令返回结果匹配的commit_explist中元素的编号
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的set_explist，commit_explist参数不是列表类型，或cmd包含'\n'
            -6: set命令出错，一般由于命令格式有问题
            -7: commit命令出错，提交失败，一般由于命令的具体逻辑问题（比如与当前配置冲突等等） 
        '''
        if type(set_explist) != list or type(set_explist) != list or cmd.rfind('\n') != -1:
            return -5
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            tel.write((cmd + '\n').encode('ascii'))
            ret = tel.expect(set_explist, timeout)
            if ret[0] == -1:
                self.close()
                return -6
            tel.write('commit\n')
            ret = tel.expect(commit_explist, timeout)
            if ret[0] == -1:
                self.close()
                return -7
            self.close()
            return ret[0]
        except EOFError as eof:
            #print eof
            self.close()
            return -4

    def send_seq_commit(self, cmds, set_explists, commit_explists, timeout=10):
        '''连接交换机，执行一系列命令并commit，此方法存在安全隐患，一旦某一部失败无法回退
        Args:
            cmds: 要执行的命令列表。
            set_explists: set命令的预期执行结果列表，每一个元素都是一个列表，对应cmds中元素。
            commit_explists: commit命令的预期执行结果列表，每一个元素都是一个列表，对应cmds中元素。
            timeout: 超时时间
        Returns:
            0: 执行结果符合预期
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 参数非法
            -6: set命令出错，一般由于命令格式有问题
            -7: commit命令出错，提交失败，一般由于命令的具体逻辑问题（比如与当前配置冲突等等） 
        '''
        if type(set_explists) != list or type(set_explists) != list or type(cmds) != list:
            return -5
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            i = 0
            while (i < len(cmds)):
                if type(set_explists[i]) != list or type(set_explists[i]) != list or\
                   cmds[i].rfind('\n') != -1:
                    return -5
                tel.write((cmds[i] + '\n').encode('ascii'))
                ret = tel.expect(set_explists[i], timeout)
                if ret[0] == -1:
                    self.close()
                    return -6
                tel.write('commit\n')
                ret = tel.expect(commit_explists[i], timeout)
                if ret[0] == -1:
                    self.close()
                    return -7
                i += 1
            self.close()
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

    def get_info_file(self, cmd, file, timeout=10):
        '''连接交换机，执行命令并将交换机输出写入文件，用于查询信息
           文件读写效率较低，且并发执行时可能导致冲突问题，推荐使用get_info_list方法
        Args:
            cmd: 要执行的命令
            timeout: 超时时间
        Returns:
            file + postfix : 输出文件名
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
        '''
        if cmd.rfind('\n') != -1:
            return -5
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            tel.write((cmd + '\n').encode('ascii'))
            time.sleep(5)
            msg = tel.read_very_eager()
            self.close()
        except EOFError as eof:
            self.close()
            return -4
        postfix = '.' + str(time.time()).replace('.', '-')
        while os.path.isfile(file + postfix):
            postfix = str(time.time()).replace('.', '-')
        f = open(file + postfix, 'w') 
        f.write(msg)
        f.close()
        return file + postfix
        

    def get_info_list(self, cmd, timeout=10):
        '''连接交换机，执行命令并将交换机输出写入列表，用于查询信息
        Args:
            cmd: 要执行的命令
            timeout: 超时时间
        Returns:
            lines : 获取到的信息按行分割形成的列表
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
        '''
        if cmd.rfind('\n') != -1:
            return -5
        try:
            ret = self.getConn()
            if ret != 0:
                return ret
            tel = self.telobj
            tel.write((cmd + '\n').encode('ascii'))
            time.sleep(5)
            msg = tel.read_very_eager()
            self.close()
        except EOFError as eof:
            self.close()
            return -4
        buffer = StringIO.StringIO(msg)
        lines = buffer.readlines()
        buffer.close()
        return lines
        

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
        cmd ='run file tftp get remote-file %s local-file rootfs.tar.gz ip-address %s'\
             % (file, tftphost) 
        #print cmd
        print self.send_nocommit(tftp, ['Done!'], 300)

    def test(self):
        ret = self.getConn()
        if ret != 0:
            return ret
        tel = self.telobj
        tel.write(('run show vlans | no-more\n').encode('ascii'))
        time.sleep(5)
        #msg = tel.read_very_eager()
        #print msg
        s = StringIO.StringIO(tel.read_very_eager()).readlines()
        #s.write(msg)
        return s

    def test2(self):
        '''test function
        '''
        t=telnetlib.Telnet('192.168.30.40')
        print t
        r=t.expect([r'login:'])
        print r[1].group()
        t.write('wangbin\n')
        r=t.expect([r'Password:'])
        print r[1].group()
        t.write('wangbin\n')
        r=t.expect([r'.*>'], 15)
        print r[1].group()
        t.write('configure\n')
        r=t.expect([r'.*#'], 15)
        print r[1].group()
        '''
        t.write('set vlans vlan-id 333\n')
        r=t.expect([r'\[edit\]'], 15)
        print r[1].group()
        t.write('commit\n')
        r=t.expect([r'Commit OK\.'], 15)
        print r[1].group()
        '''
        t.write('run show vlans vlan-id 444\n')
        r=t.expect([r'syntax error, expecting.*'], 15)
        print r[1].group()
        print r[2]
        t.close()

if __name__ == '__main__':
    t = TelnetXorplus('192.168.30.16', 'admin', 'admin')
    '''
    t.send_commit('set vlans vlan-id 111', [r'\[edit\]\s+.*#'], [r'Commit OK\.\s+\[edit\]\s+.*#'])
    str = 'VLAN ID: 111 \r\r\n\
VLAN Name: default \r\r\n\
Description:  \r\r\n\
vlan-interface:  \r\r\n\
Number of member ports: 0 \r\r\n\
Tagged port: None\r\r\n\
Untagged port: None'
    print t.send_nocommit('run show vlans vlan-id 111', [str])
    '''  
    #tftp = 'tftp -g -l rootfs.tar.gz -r %s 192.168.30.92' % (file)
    ####print t.shell_cmd(['cd /cftmp', tftp])
    #t.update_system('192.168.30.92', 'rootfs-d2020_1-0-8-5.tar.gz')
    
    print t.test()
    #print s.getvalue()
    #s.seek(0)
    #for line in s.readlines():
    #    print line
