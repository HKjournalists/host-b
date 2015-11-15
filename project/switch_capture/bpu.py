# -*- coding:utf8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
Breakpoint processing unit
Authors: wangbin19@baidu.com
Date:    2015/11/13 14:53:50
Todo:    
"""

import re
import socket
import struct
import pexpect
import traceback

class Bpu(object):
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.prompt = r'\n\(gdb\)\W'

    def gdbcmd(self, sh, cmd):
        """执行gdb命令并匹配回显命令
        Args:
            sh: gdb连接对象
            cmd: 命令
        Returns:
            index: 匹配到的模式序号
        """
        sh.sendline('%s\r' % (cmd))
        index = sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT], 1)
        if index == 0:
            before = sh.before.replace('\x00', '').strip()
            after = sh.after.replace('\x00', '').strip()
            if self.verbose:
                print('%sBEFORE%s\n%s\n%sCMD%s\n%s\n%sEND%s' % 
                      ('#'*8, '#'*8, before, '@'*8, '@'*8, after, '#'*8, '#'*8))
        return index

    def gdbcmd_loop(self, sh, cmd, pattern):
        """循环执行gdb命令直到匹配到指定模式
        Args:
            sh: gdb连接对象
            cmd: 命令
            pattern: 需要匹配的模式
        Returns:
            before: 匹配到的内容
        """
        sh.sendline(cmd)
        index = sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT], 1)
        if index == 0:
            before = sh.before.replace('\x00', '').strip()
            after = sh.after.replace('\x00', '').strip()
            if self.verbose:
                print('%sBEFORE%s\n%s\n%sCMD%s\n%s\n%sEND%s' % 
                      ('#'*8, '#'*8, before, '@'*8, '@'*8, after, '#'*8, '#'*8))
        while True:
            index = sh.expect([pattern, pexpect.EOF, pexpect.TIMEOUT], 1)
            if index == 0:
                before = sh.before.replace('\x00', '').strip()
                after = sh.after.replace('\x00', '').strip()
                if self.verbose:
                    print('%sBEFORE%s\n%s\n%sPATTERN%s\n%s\n%sEND%s' % 
                          ('#'*8, '#'*8, before, '@'*8, '@'*8, after, '#'*8, '#'*8))
                return before.replace('\r', '')
            if index == 1:
                break
            sh.sendline(cmd)
            sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT], 1)

    def get_handler(self, name):
        """通过自省动态加载方法
        Args:
            name: 方法名
        Returns:
            handler: 获取到的方法
            None: 找不到方法时返回None
        """
        if hasattr(self, name):
            handler = getattr(self, name)
            if not hasattr(handler, '__call__'):
                return None
            return handler
    
    def pxvec_ospf(self, sh, name):
        """按16进制打印vector型变量
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            pkt: 打印出的16进制信息
        """
        self.gdbcmd(sh, 'p %s' % (name))
        index = sh.expect([r'_M_start = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([r'_M_finish = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        eaddr = sh.match.group(1)
        index = sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        l = int(eaddr, 16) - int(saddr, 16)
        cmd = 'x/%dxb %s' % (l, saddr)
        pkt = self.gdbcmd_loop(sh, cmd, self.prompt).decode('utf-8')
        return pkt

    def pxvec_lcmgrcb(self, sh, name):
        """按16进制打印vector型变量
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            pkt: 打印出的16进制信息
            None: 当前包非ospf包，返回None
        """
        self.gdbcmd(sh, 'p %s' % (name))
        index = sh.expect([r'_M_start = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([r'_M_finish = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        eaddr = sh.match.group(1)
        index = sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        l = int(eaddr, 16) - int(saddr, 16)
        cmd = 'x/%dxb %s' % (l, saddr)
        pkt = self.gdbcmd_loop(sh, cmd, self.prompt).decode('utf-8')
        if not self.pktfilter(pkt, [27], r'^59$'):    #过滤ospf包
            return None
        return pkt

    def pxvec_fea(self, sh, name):
        """按16进制打印vector型变量
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            pkt: 打印出的16进制信息
            None: 当前包非ospf包，返回None
        """
        self.gdbcmd(sh, 'p %s' % (name))
        index = sh.expect([r'_M_start = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([r'_M_finish = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        eaddr = sh.match.group(1)
        index = sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        l = int(eaddr, 16) - int(saddr, 16)
        cmd = 'x/%dxb %s' % (l, saddr)
        pkt = self.gdbcmd_loop(sh, cmd, self.prompt).decode('utf-8')
        if not self.pktfilter(pkt, [0, 1], r'^020[1-5]$'):    #过滤ospf包
            return None
        return pkt

    def pcls_lcmgrcb(self, sh, name):
        """按16进制打印class中的vector型变量
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            pkt: 打印出的16进制信息
            None: 当前包非ospf包，返回None
        """
        p_clsaddr = re.compile(r'.*\(.*(?:(\b\w+) [\*&])\) @?(0x\w+)', re.S)
        var = self.gdbcmd_loop(sh, 'p %s' % (name), self.prompt)
        (cls, addr) = p_clsaddr.match(var).groups()
        sh.sendline('p {%s} %s\r' % (cls, addr))
        sh.expect(['p {%s} %s' % (cls, addr), pexpect.EOF, pexpect.TIMEOUT], 1)
        index = sh.expect(['_pkt_data', pexpect.EOF, pexpect.TIMEOUT])
        index = sh.expect([r'_M_start = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([r'_M_finish = (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        eaddr = sh.match.group(1)
        index = sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        l = int(eaddr, 16) - int(saddr, 16) 
        cmd = 'x/%dxb %s' % (l, saddr)
        pkt = self.gdbcmd_loop(sh, cmd, self.prompt).decode('utf-8')
        if not self.pktfilter(pkt, [27], r'^59$'):    #过滤ospf包
            return None
        return pkt

    def parr_ospf(self, sh, name):
        """按16进制打印uint8_t*型变量
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            pkt: 打印出的16进制信息
        """
        self.gdbcmd(sh, 'p %s' % (name))
        index = sh.expect([r'\(.*\) (0x\w+) "', pexpect.EOF, pexpect.TIMEOUT])
        saddr = sh.match.group(1)
        index = sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)  
        ret = self.gdbcmd_loop(sh, 'p len', self.prompt)
        l = int(re.match(r'\$\d+ = (\d+)', ret).group(1))
        cmd = 'x/%dxb %s' % (l, saddr)
        pkt = self.gdbcmd_loop(sh, cmd, self.prompt)
        return pkt.decode('utf-8')

    def pip(self, sh, name):
        """打印整数形式的ip地址
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            msg: 变量名+ip地址
        """
        p_clsaddr = re.compile(r'.*\(.*(?:(\b\w+) [\*&])\) @?(0x\w+)', re.S)
        var = self.gdbcmd_loop(sh, 'p %s' % (name), self.prompt)
        (cls, addr) = p_clsaddr.match(var).groups()
        self.gdbcmd_loop(sh, 'p {%s} %s' % (cls, addr), r'_addr = (\w+)\}')
        ip_int = int(sh.match.group(1))
        ip = socket.inet_ntoa(struct.pack('I', socket.htonl(ip_int)))
        sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        msg = '%s: %s' % (name, ip)
        return msg

    def pipvx(self, sh, name):
        """打印IPvX形式的ip地址
        Args:
            sh: gdb连接对象
            name: 变量名
        Returns:
            msg: 变量名+ip地址
        """
        p_clsaddr = re.compile(r'.*\(.*(?:(\b\w+) [\*&])\) @?(0x\w+)', re.S)
        var = self.gdbcmd_loop(sh, 'p %s' % (name), self.prompt)
        (cls, addr) = p_clsaddr.match(var).groups()
        self.gdbcmd_loop(sh, 'p {%s} %s' % (cls, addr), r'_addr = \{(\w+)\,')
        ip_int = int(sh.match.group(1))
        ip = socket.inet_ntoa(struct.pack('I', socket.htonl(ip_int)))
        sh.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT], 1)
        msg = '%s: %s' % (name, ip)
        return msg
        
    def pktfilter(self, buf, pos, patt):
        """数据包过滤器
        Args:
            buf: 数据包
            pos: 需要判断的字节位置（数组形式，可判断连续多个字节）
            filter_patt: 判断用的正则表达式
        """
        #filter_dict = {
        #    'l2_lcmgrcb': {'pos': [27], 'patt': r'^59$'},
        #    'l2_lcmgrbuf': {'pos': [51], 'patt': r'^59$'},
        #    'l2_sif': {'pos': [27], 'patt': r'^59$'},
        #    'l4_fea': {'pos': [0, 1], 'patt': r'^020[1-5]$'}
        #}
        i = 0
        j = 0
        ret = ''
        #flags = filter_dict[proto]['pos']
        filter_patt = re.compile(patt)
        pattern = re.compile(r'^0x(\w{2})$')
        flag = pos.pop(0)
        for byte in buf.split():
            m = pattern.match(byte.strip())
            if m is None:
                continue
            if i == flag:
                ret += m.group(1)
                if not pos:
                    break
                flag = pos.pop(0)
                j += 1
            i += 1
        if filter_patt.match(ret) is not None:
            return True
        return False   