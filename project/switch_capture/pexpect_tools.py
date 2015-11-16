# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
交换机pexpect库

Authors: wangbin19@baidu.com
Date:    2015/10/14 16:28:35
Todo:    加入自定义异常
"""

import re
import sys
import string
import pexpect
import traceback

class PexpcError(BaseException):
    '''自定义异常类
    info: 异常信息
    '''
    def __init__(self, info):
        self.info = info
    
    def __str__(self):
        return '%s' % (self.info)

class Pexpc4Xorplus(object):
    """基于pexpect的交换机telnet库
    Attributes:
        ip: 交换机管理ip
        username: 交换机管理用户名
        password: 交换机管理密码
        sh_password: 交换机shell密码
        root_password: 交换机shell的root用户密码
        expsh: shell连接对象
    """
    def __init__(self, ip, username, password, sh_password, root_password):
        self.ip = ip
        self.username = username
        self.password = password
        self.sh_password = sh_password
        self.root_password = root_password
        self.timeout = 30
        self.expsh = None

    def start_sh(self):
        """使用pexpect通过telnet连接交换机，进入shell会话
        Args:
            None
        Returns:
            child: pexpect子进程（开启交换机shell会话）
            None: 进入shell过程中出错则返回None
        """
        if self.expsh is not None and self.expsh.isalive():
            return child
        child = pexpect.spawn('telnet %s' % (self.ip), timeout=self.timeout)
        index = child.expect(['login:', '.*>', pexpect.EOF, pexpect.TIMEOUT])
        if index > 1:
            child.close(force=True)
            return None
        if index == 0:
            child.sendline(self.username)
            index = child.expect(['[pP]assword', pexpect.EOF, pexpect.TIMEOUT])
            if index != 0:
                child.close(force=True) 
                return None
            child.sendline(self.password)
            index = child.expect(['.*>', pexpect.EOF, pexpect.TIMEOUT])
            if index != 0:
                child.close(force=True) 
                return None
        child.sendline('start shell sh')
        index = child.expect(['Input password:', pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            child.close(force=True) 
            return None
        child.sendline(self.sh_password)
        index = child.expect(['$', pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            child.close(force=True)
            return None
        child.sendline('su root')
        index = child.expect(['Password:', pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            child.close(force=True)
            return None
        child.sendline(self.root_password)
        index = child.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            child.close(force=True)
            return None
        self.expsh = child
        return child

    def send_sh(self, cmd, pattern):
        """Send a command to swith, seek through the stream until a pattern is matched.
        Args:
            cmd: 发送的命令
            pattern: The pattern must be a list of StringType and compiled re.
                     pattern为None时，只发送命令不进行匹配
        Returns:
            index: The index into the pattern list
        """
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        patterns = [pexpect.EOF, pexpect.TIMEOUT]
        self.expsh.sendline(cmd)
        if pattern is None:
            return 0  
        for p in pattern[: : -1]:
            patterns.insert(0, p)      
        index = self.expsh.expect(patterns)
        if index == len(patterns) - 2:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == len(patterns) - 1:
            raise PexpcError, 'command timeout: %s' % (cmd)
        return index
    
    def send_sh2(self, cmds, pattern):
        """Send several commands to swith, when the last command has been sent,
           seek through the stream until a pattern is matched.
        Args:
            cmds: 待执行的命令列表
            pattern: The pattern must be a list of StringType and compiled re.
        Returns:
            index: The index into the pattern list
        """
        if type(cmds) != list:
            raise PexpcError, 'invalid parameter: %s' % (cmd)
        if type(pattern) != list:
            raise PexpcError, 'invalid parameter: %s' % (pattern)
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        patterns = [pexpect.EOF, pexpect.TIMEOUT]
        for p in pattern[: : -1]:
            patterns.insert(0, p)
        temp_pattern = [r'#', pexpect.EOF, pexpect.TIMEOUT]
        length = len(cmds)
        i = index = 0
        for i in range(length):
            if i == length - 1:
                temp_pattern = patterns
            self.expsh.sendline(cmds[i])
            #print('cmd: %s ; pattern: %s' % (cmds[i], temp_pattern))
            index = self.expsh.expect(temp_pattern)
            #print('index of matched pattern: %d' % (index))
            #print('ouput of child process: %s' % (self.expsh.before.strip()))
            if i < length - 1 and index != 0:
                raise PexpcError, 'command failed: %s' % (cmds[i])
        if index == len(patterns) - 2:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == len(patterns) - 1:
            raise PexpcError, 'command timeout: %s' % (cmd)
        #如果最后一个命令匹配的不是命令行提示符'#'，则需要在下次调用expect前额外匹配一次'#'，
        #因为每条指令执行后shell都会输出一个命令行提示符，因此需要从子进程中将其读出，
        #否则将影响下一次expect执行（重要，被坑了一个晚上）
        if temp_pattern[index] != '#':
            temp = self.expsh.expect([r'#', pexpect.EOF, pexpect.TIMEOUT])
            if temp == len(patterns) - 2:
                raise PexpcError, 'recieve EOF in command %s ' % (cmd)
            elif temp == len(patterns) - 1:
                raise PexpcError, 'command timeout: %s' % (cmd)
        return index

    def send_echo(self, cmd, prompt):
        """发送命令，获取提示符之前的所有输出
        Args:
            cmd: 发送的命令
            prompt: 提示符，用于标示获取内容结束的标志
        Returns:
            before: 提示符之前的内容
            after: 提示符
        """
        if type(cmd) != str:
            raise PexpcError, 'invalid parameter: %s' % (cmd)
        if type(prompt) != str:
            raise PexpcError, 'invalid parameter: %s' % (prompt)
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        self.expsh.sendline(cmd)
        #清除echo回显的命令
        self.expsh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
        index = self.expsh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
        if index == 1:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == 2:
            raise PexpcError, 'command timeout: %s' % (cmd)
        before = self.expsh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
        after = self.expsh.after.replace('\x00', '').strip()
        return (before, after)

    def send_echo2(self, cmd, pattern, prompt):
        """发送命令，获取匹配到的内容
        Args:
            cmd: 发送的命令
            prompt: 提示符，用于标示获取内容结束的标志
            pattern: The pattern must be a StringType and compiled re
        Returns:
            before: 提示符之前的内容
            after: 提示符
        """
        if type(cmd) != str:
            raise PexpcError, 'invalid parameter: %s' % (cmd)
        if type(pattern) != str and not isinstance(pattern, type(re.compile(''))):
            raise PexpcError, 'invalid parameter: %s' % (pattern)
        if type(prompt) != str:
            raise PexpcError, 'invalid parameter: %s' % (prompt)
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        self.expsh.sendline(cmd)
        #清除echo回显的命令
        self.expsh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
        #print self.expsh.before.replace('\x00', '').strip()
        index = self.expsh.expect([pattern, pexpect.EOF, pexpect.TIMEOUT])
        if index == 1:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == 2:
            raise PexpcError, 'command timeout: %s' % (cmd)
        after = self.expsh.after.replace('\x00', '').strip()
        index = self.expsh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
        if index == 1:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == 2:
            raise PexpcError, 'command timeout: %s' % (cmd)
        #before = self.expsh.before.replace('\x00', '').strip()  
        return after

    def send_expect(self, pattern):
        """Seek through the stream until a pattern is matched.
        Args:
            pattern: The pattern must be a list of StringType and compiled re.
        Returns:
            index: 匹配到的pattern
        """
        if type(pattern) != list:
            raise PexpcError, 'invalid parameter: %s' % (pattern)
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        patterns = [pexpect.EOF, pexpect.TIMEOUT]
        for p in pattern[: : -1]:
            patterns.insert(0, p)
        index = self.expsh.expect(patterns)
        if index == len(patterns) - 2:
            raise PexpcError, 'recieve EOF in command %s ' % (cmd)
        elif index == len(patterns) - 1:
            raise PexpcError, 'command timeout: %s' % (cmd)
        return index

    def exp_echo(self, pattern):
        """不发送命令，只从子进程匹配pattern并返回匹配到的内容
        Args:
            pattern: The pattern must be a StringType and compiled re
        Returns:
            after: 匹配到的内容
        """
        if type(pattern) != str and not isinstance(pattern, type(re.compile(' '))):
            raise PexpcError, 'invalid parameter: %s' % (pattern)
        if self.expsh is None or not self.expsh.isalive():
            raise PexpcError, 'invalid connection'
        index = self.expsh.expect([pattern, pexpect.EOF, pexpect.TIMEOUT])
        if index == 1:
            raise PexpcError, 'recieve EOF in child thread'
        elif index == 2:
            raise PexpcError, 'child thread timeout'
        after = self.expsh.after.replace('\x00', '').strip()
        return after
        
    def file_exists(self, dir, file):
        """判断指定目录下是否存在某一文件
        Args:
            dir: 目录绝对路径
            file: 文件名
        Returns:
            True: 存在
            False: 不存在
        """
        params = locals()
        for key in [k for k in params if k != 'self']:
            if type(params[key]) != str:
                raise PexpcError, 'invalid parameter: %s' % (params[key])
        cmds = []
        cmds.append('cd %s' % (dir))
        cmds.append('ls | grep -q "^%s$"' % (file))
        cmds.append('echo $?')
        try:
            ret = self.send_sh2(cmds, [r'0', r'1'])
        except PexpcError, e:
            raise PexpcError, e.info
        if ret == 0:
            return True
        elif ret == 1:
            return False

    def file_check(self, dir, file, postfix='.bak'):
        """判断指定目录下是否存在某一文件，若存在则将其备份
        Args:
            dir: 目录绝对路径
            file: 文件名
            postfix: 备份后缀名
        Returns:
            0: 不存在同名文件
            1: 存在同名文件并已备份
        """
        params = locals()
        for key in [k for k in params if k != 'self']:
            if type(params[key]) != str:
                raise PexpcError, 'invalid parameter: %s' % (params[key])
        try:
            ret = self.file_exists(dir, file)
            if ret:
                cmds = []
                cmds.append('cd %s' % (dir))
                cmds.append('mv %s %s%s' % (file, file, postfix))
                ret = self.send_sh2(cmds, [r'#'])
                return 1
        except PexpcError, e:
            raise PexpcError, e.info
        return 0  

    def file_scp(self, src, dst, username, password, recursion=False, reverse=False):
        """使用scp复制文件
        Args:
            src: 源地址
            dst: 目的地址
            username: 远端主机用户名
            password: 远端主机密码
            recursion: 是否使用-r参数（用于复制整个文件夹）
            reverse: 值为False时，从远端复制到交换机；值为True时，从交换机复制到远端
        Returns:
            0: 正常
        """
        params = locals()
        for key in ['src', 'dst', 'username', 'password']:
            if type(params[key]) != str :
                raise PexpcError, 'invalid parameter: %s' % (params[key])
        for key in ['recursion', 'reverse']:
            if type(params[key]) != bool :
                raise PexpcError, 'invalid parameter: %s' % (params[key])
        cmd = 'scp -r ' if recursion else 'scp '
        cmd += '%s %s@%s' % (src, username, dst) if reverse else '%s@%s %s' % (username, src, dst)
        try:
            index = self.send_sh(cmd, [r'.*\(yes/no\)\?', r'\(y/n\)' , r'.*password:'])
            if index == 0 or index == 1:
                self.send_sh('yes', [r'.*password:'])
            self.send_sh(password, [r'#'])
        except PexpcError, e:
            raise PexpcError, e.info
        return 0   

    def single_cmd(self, cmd, pattern, prompt=r'#'):
        """发送单条指令（send_sh()的包装函数）
            Args:
            cmd: 发送的命令
            prompt: 命令提示符，若传入None则不检查命令提示符
            pattern: The pattern must be a list of StringType and compiled re. 
                     pattern为None时，只发送命令不进行匹配
        Returns:
            index: The index into the pattern list
        """
        if type(cmd) != str:
            raise PexpcError, 'invalid parameter: %s' % (cmd)
        if type(pattern) != list and pattern is not None:
            raise PexpcError, 'invalid parameter: %s' % (pattern)
        if type(prompt) != str and prompt is not None:
            raise PexpcError, 'invalid parameter: %s' % (prompt)
        #print('cmd: %s ; pattern: %s' % (cmd, pattern))
        try:
            index = self.send_sh(cmd, pattern)
            if prompt is not None and pattern[index] != prompt:
                self.send_expect([prompt])
        except PexpcError, e:
            raise PexpcError, e.info
        return index 

    def set_timeout(self, time):
        """设置超时时间
        Args:
            time: 超时时间（秒）
        Returns:
            0: 成功
        """
        self.timeout = time
        return 0
    
    def close_sh(self, sh=None):
        """关闭pexpect连接
        Args:
            None
        Returns:
            0: 成功
        """
        if sh is not None:
            sh.sendline('exit')
            sh.expect(['$', pexpect.EOF, pexpect.TIMEOUT], 5)
            sh.sendline('exit\n')
            sh.expect(['.*>', pexpect.EOF, pexpect.TIMEOUT], 5)
            sh.sendline('exit')
            sh.expect([['.*[$#]', pexpect.EOF, pexpect.TIMEOUT], pexpect.EOF], 5)
            return 0
        if self.expsh is not None and self.expsh.isalive():
            try:
                self.expsh.sendline('exit')
                index = self.expsh.expect(['$', pexpect.EOF, pexpect.TIMEOUT], 5)
                if index != 0:
                    return -1 
                self.expsh.sendline('exit\n')
                index = self.expsh.expect(['.*>', pexpect.EOF, pexpect.TIMEOUT], 5)
                if index != 0:
                    return -1 
                self.expsh.sendline('exit')
                index = self.expsh.expect(['.*[$#]', pexpect.EOF, pexpect.TIMEOUT], 5)
                if index != 1:
                    return -1 
                return 0        
            finally:
                self.expsh.close(force=True)
                self.expsh = None

    def test(self, child, cmd, pattern, ev):
        child.sendline(cmd)
        child.expect([cmd, pexpect.EOF, pexpect.TIMEOUT], con.timeout)
        while True:
            index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], con.timeout)
            if index == 0:
                before = sh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
                after = sh.after.replace('\x00', '').strip()
                return (before, after)
            if index == 1:
                return None
            if ev.is_set():
                return None

if __name__ == '__main__':
    con = Pexpc4Xorplus('192.168.30.25', 'admin', 'admin', 'toor', 'toor')
    sh = con.start_sh()
    #ret = con.file_scp('192.168.30.92:/home/wangbin/project/switch_capture/logs/lcmgr.log',
    #           '/tmp/', 'wangbin', 'ljfl2zql')
    #ret = con.file_scp('192.168.30.92:/home/wangbin/project/switch_capture/logs/',
    #           '/tmp/', 'wangbin', 'ljfl2zql', True)
    #ret = con.file_scp('192.168.30.92:/home/wangbin/project/switch_capture/logs/',
    #           '/tmp/', 'wangbin', 'ljfl2zql', True)
    #ret = con.file_scp('/tmp/home/', '192.168.30.92:/home/wangbin/project/switch_capture/logs/',
    #           'wangbin', 'ljfl2zql', True, True)
    #ret = con.file_exists('/lib', 'libpam.so')
    #ret = con.file_check('/lib', 'libpam.so')
    #(before, after) = p.send_echo('gdb', r'\n\(gdb\)\W')
    #print('before:\n%s\n###############\nafter:\n%s' % (before, after))
    prompt = r'\n\(gdb\)\W'
    ret = con.send_echo('cd /pica/bin/sif', r'#')
    pid = con.send_echo('pgrep pica_sif', r'#')[0]    #获取pid
    #ret = con.send_echo('gdb attach %s' % (pid), prompt)   #进入gdb
    #print ret[0]
    cmd = 'gdb attach %s' % (pid)
    sh.sendline(cmd)
    index = sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print sh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
        print sh.after.replace('\x00', '').strip()
    index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print sh.before.replace('\x00', '').strip()
        print sh.after.replace('\x00', '').strip()

    #ret = con.single_cmd('source /pica/bin/sif/sif.gdb', [r'\(y or n\)', prompt], None)
    #index = con.send_sh('source /pica/bin/sif/sif.gdb', [r'\(y or n\)', prompt])
    #print con.expsh.before.replace('\x00', '').strip()
    cmd = 'source /pica/bin/sif/sif.gdb'
    sh.sendline(cmd)
    index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print sh.before.replace('\x00', '').strip()
        print sh.after.replace('\x00', '').strip()
    while True:
        #ret = con.send_echo2('c', r'Breakpoint \d+,', prompt)  #断点编号
        #ret = con.send_echo('c', prompt)
        sh.sendline('c')
        index =sh.expect(['c', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print sh.before.replace('\x00', '').strip()
            print sh.after.replace('\x00', '').strip()
        index = sh.expect(['Breakpoint (\d+),', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print sh.before.replace('\x00', '').strip()
            print sh.after.replace('\x00', '').strip()
            #print sh.match.group(1)
        index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print sh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
            print sh.after.replace('\x00', '').strip()

        #con.single_cmd('p payload', None, None)
        #ret = con.exp_echo(r'%s = 0x\w+ "' % ('_M_start')) 
        #saddr = re.match(r'%s = (0x\w+)' % ('_M_start'), ret).group(1)  #起始地址
        #print con.expsh.before.replace('\x00', '').strip()
        #ret = con.exp_echo(r'%s = 0x\w+ "' % ('_M_finish'))
        #eaddr = re.match(r'%s = (0x\w+)' % ('_M_finish'), ret).group(1) #末尾地址
        #print con.expsh.before.replace('\x00', '').strip()
        #con.exp_echo(prompt)
        #print con.expsh.before.replace('\x00', '').strip()
        cmd = 'p payload'
        sh.sendline(cmd)
        index = sh.expect([r'_M_start = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([r'_M_finish = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        eaddr = sh.match.group(1)
        index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], con.timeout)

        l = int(eaddr, 16) - int(saddr, 16)   #vector数据部分长度
        #print l
        cmd = 'x/%dxb %s' % (l, saddr)
        #ret = con.send_echo(cmd, prompt)
        #print ret[0]
        sh.sendline(cmd)
        index = sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print sh.before.replace('\x00', '').strip()
            print sh.after.replace('\x00', '').strip()
        index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 5)
        #print index
        while True:
            index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 5)
            #print index
            if index == 0:
                print sh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
                print sh.after.replace('\x00', '').strip()
                break
            if index == 1:
                break
            sh.sendline(cmd)
            sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
        #break
    #ret = con.expsh.send_echo('q', r'\(y or n\)')  #退出gdb
    #print ret[0]
    #ret = con.expsh.send_echo('y', r'#') 
    #print ret[0]
    sh.sendline('q')
    sh.expect(['q', pexpect.EOF, pexpect.TIMEOUT])
    index = sh.expect(r'\(y or n\)', con.timeout)

    sh.sendline('y')
    sh.expect(['y', pexpect.EOF, pexpect.TIMEOUT])
    index = sh.expect(r'#', con.timeout)

    con.close_sh(sh)
    #print ret
    #try:
    #    raise PexpcError, 'Test error'
    #except PexpcError, e:
    #    print e.info
    #    traceback.print_exc(file=sys.stdout)
