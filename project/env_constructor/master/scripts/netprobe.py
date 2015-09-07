# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
网络探测工具
Authors: wangbin19@baidu.com
Date:    2015/07/20 20:47:06
"""
import re
import os
import sys
import socket
import struct
import subprocess
from scapy.all import srp, arping
from scapy.layers.l2 import Ether, ARP

import ssh_tools

class NetProbe(object):
    def __init__(self, ip, uname, passwd):
        '''构造方法
        Args:
            ip: 目标设备的管理ip
            uname: 用户名（需要root权限）
            passwd: 密码
        Returns:
            None
        '''
        self.ip = ip
        self.uname = uname
        self.passwd = passwd
        self.local = None

    @staticmethod
    def mask2int(mask):
        '''子网掩码由点分十进制字符串转换为整数
        Args:
            mask: 点分十进制字符串形式的掩码
        Returns:
            sum(count): 整数形式的掩码
            -1: mask类型非法
            -2: mask格式非法
        '''
        if type(mask) != str:
            return -1
        regex = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'
        if re.match(regex, mask) is None:
            return -2
        # 计算二进制字符串中 '1' 的个数
        count1 = lambda str: len([i for i in str if i == '.'])
        # 分割字符串格式的子网掩码为四段列表
        submask = mask.split('.')
        # 转换各段子网掩码为二进制字符串, 分别计算其中'1'的个数
        count = [count1(bin(int(i))) for i in submask]
        return sum(count)  #数组求和并返回

    @staticmethod
    def mask2str(mask):
        '''子网掩码由整数形式转换为点分十进制字符串
        Args:
            mask: 整数形式的掩码
        Returns:
            ".".join(list): 点分十进制字符串形式的掩码
            -1: mask类型非法
            -2: mask格式非法
            -3: mask超出范围
        '''
        if type(mask) != str and type(mask) != int:
            return -1
        elif(type(mask) == str):
            if re.match(r'^([0-9]|([1-2][0-9])|(3[0-2]))$', mask) is None:
                return -2
            mask = int(mask)
        elif(type(mask) == int):
            if mask < 0 or mask > 32:
                return -3
        #创建一个全'0'的32位字符数组
        bits = ['0' for i in range(32)] 
        #按照掩码将相应位置置为'1'   
        for i in range(mask):
            bits[i] = '1'
        #每8位拼接为一个二进制形式的字符串                
        list = [''.join(bits[i * 8:i * 8 + 8]) for i in range(4)]  
        #每个字符串以十进制形式输出，再转换为字符串 
        list = [str(int(item, 2)) for item in list]  
        return '.'.join(list)  #拼接为点分十进制字符串

    @staticmethod
    def belongto(ip, subnet):
        '''判断指定ip是否属于某一subnet网段
        Args:
            ip: 待判断ip（如192.168.1.1）
            subnet: 待判断的网段（如192.168.1.0/24）
        Returns:
            True: ip属于subnet所在网段
            False: ip不属于subnet所在网段
            -1: mask类型非法
            -2: mask格式非法
            -3: mask超出范围
        '''
        (subnet, mask) = subnet.split('/')
        if ip == subnet:
            return True
        #ip转换为int
        intip = socket.ntohl(struct.unpack('I', socket.inet_aton(ip))[0]) 
        #mask转换为点分十进制
        mask = NetProbe.mask2str(mask)
        if type(mask) == int:
            return mask 
        #mask转换为int
        intmask = socket.ntohl(struct.unpack('I', socket.inet_aton(mask))[0])
        #ip和mask进行按位与运算，转换回点分十进制
        ipnet = socket.inet_ntoa(struct.pack('I', socket.htonl(intip & intmask)))  
        if ipnet == subnet:
            return True
        return False

    @staticmethod
    def getsubnet(inet):
        '''由ip/mask转化为子网/mask（如1.1.1.1/24转化为1.1.1.0/24）
        Args:
            inet: ip/mask
        Returns:
            subnet: 子网/mask
            -1: mask类型非法
            -2: mask格式非法
            -3: mask超出范围
            -4: 参数inet错误
        '''
        if type(inet) != str:
            return -4
        (ip, mask) = inet.split('/')
        r_ip = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'
        r_mask = r'^([0-9]|([1-2][0-9])|(3[0-2]))$'
        if re.match(r_ip, ip) is None or re.match(r_mask, mask) is None:
            return -4
        intip = socket.ntohl(struct.unpack('I', socket.inet_aton(ip))[0])
        tmp = NetProbe.mask2str(mask)
        if type(tmp) == int:
            return tmp
        intmask = socket.ntohl(struct.unpack('I', socket.inet_aton(tmp))[0])
        ipnet = socket.inet_ntoa(struct.pack('I', socket.htonl(intip & intmask)))
        subnet = ipnet + '/' + mask
        return subnet

    @staticmethod
    def samenet(src, dst):
        '''判断src与dst是否是同一子网
        Args:
            src: 源ip
            dst: 目的ip
        Returns:
            True/False: 是/否
            -1: 子网格式错误
        '''
        snet = src.split('/')[0]
        smask = src.split('/')[1]
        dnet = dst.split('/')[0]
        dmask = dst.split('/')[1]
        mask = smask if smask < dmask else dmask
        snet = NetProbe.getsubnet(snet + '/' + mask)
        #print('snet: ' + snet)
        if type(snet) == int:
            return -1
        dnet = NetProbe.getsubnet(dnet + '/' + mask)
        #print('dnet: ' + dnet)
        if type(dnet) == int:
            return -1
        return snet == dnet

    @staticmethod
    def ipgen(inet):
        '''根据指定子网的ip地址生成一个相近地址
        Args:
            inet: 待处理的子网地址
        Returns:
            inet: 处理后的子网地址
            -1: 子网地址非法
        '''
        ip = inet.split('/')[0]
        mask = inet.split('/')[1]
        r_ip = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'
        r_mask = r'^([0-9]|([1-2][0-9])|(3[0-2]))$'
        if re.match(r_ip, ip) is None or re.match(r_mask, mask) is None:
            return -1
        tmp = int(ip.split('.')[3])
        if tmp == 243:
            tmp -= 11
        else:
            tmp += 11
        inet = '.'.join(ip.split('.')[:3]) + '.' + str(tmp) + '/' + mask
        return inet

    def islocal(self):
        '''判断目标主机是否就是本机
        Args:
            None
        Returns:
            True: 是
            False: 否
        '''
        nets = []
        sp = subprocess.Popen('ip a', shell=True, stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if err != '':
            return (-5, err)
        else:
            lines = out.split(os.linesep) 
        for net in lines:
            net = net.split()
            if 'inet' in net:             #读取本机网卡信息
                nets.append(net[1])
        for net in nets:
            if NetProbe.belongto(self.ip, net):   #判断目标主机是否就是本机
                self.local = True
                return True
        self.local = False
        return False

    def getnets(self):
        '''获取目标主机所有网卡的ip子网信息
        Args:
            None
        Returns:
            nets: 主机直连的接口和网段信息，格式为{'eth0': ['1.1.1.1/24', ...]}
            -5: subprocess出错
            lines: 参考ssh_tools.get_cmd_ret()方法的返回值
        '''
        nets = []
        sp = subprocess.Popen('ip a', shell=True, stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if err != '':
            return (-5, err)
        else:
            lines = out.split(os.linesep) 
        for net in lines:
            net = net.split()
            if 'inet' in net:             #读取本机网卡信息
                nets.append(net[1])
        for net in nets:
            if NetProbe.belongto(self.ip, net):   #判断目标主机是否就是本机
                self.local = True
                break
        #目标主机为本地主机，则使用刚才获取的信息；目标主机为远程主机，则使用ssh重新获取信息 
        if not self.local:                                
            ssh = ssh_tools.SshConnect(self.ip, self.uname, self.passwd)   
            lines = ssh.get_cmd_ret('ip a') 
            if type(lines) == int:
                return lines 
        devnets = {}  #{'网卡1': ['ip/mask', ...], '网卡2': ['ip/mask', ...], ...}
        i = 0
        while i < len(lines) and lines[i] != '':
            inets = []
            line = lines[i].split()
            dev = line[1].split(':')[0]
            i += 2
            while i < len(lines) and lines[i] != ''\
                                 and lines[i].split()[0] == 'inet':
                inets.append(lines[i].split()[1])
                i += 1
            while i < len(lines) and lines[i] != ''\
                                 and re.match(r'\d+:', lines[i].split()[0]) is None:
                i += 1
            devnets[dev] = inets
        return devnets

    def getdevs(self):
        '''查询远程主机网卡信息
        Args:
            无
        Returns:
            -1: 连接服务器出错
            -2: socket超时
        '''
        ifs = []
        ssh = ssh_tools.SshConnect(self.ip, self.uname, self.passwd)   
        lines = ssh.get_cmd_ret('ip a')
        if type(lines) == int:
            return lines   
        i = 0
        while i < len(lines):
            interface = {'dev': '0', 'state': 'DOWN', 'mac': '0', 'addrs': []}
            line = lines[i].split()
            interface['dev'] = line[1].split(':')[0]
            if 'UP' in line[2].split(','):
                interface['state'] = 'UP'
            interface['mac'] = lines[i + 1].split()[1]
            i += 2
            while i < len(lines) and lines[i].split()[0] == 'inet':
                interface['addrs'].append(lines[i].split()[1])
                i += 1
            while i < len(lines) and re.match(r'\d+:', lines[i].split()[0]) is None:
                i += 1
            ifs.append(interface)
        return ifs

    def scanbrs(self):
        '''扫描网段，获取邻居信息
        Args:
            None
        Returns:
            devnbrs: 每个网络接口直连设备的信息，格式为：
                     [{'dev': '接口1', nbrs: [{'ip': '邻居ip', 'mac': '邻居mac'}, ...]}, ...]
            其他：参考ssh_tools.get_cmd_ret()、self.getsubnet()的返回值
        '''
        devnbrs = []
        devnets = self.getnets()
        for dev in self.getnets():
            if dev == 'lo' or devnets[dev] == []:
                continue
            devnbr = {'dev': dev, 'nbrs': []}
            for inet in devnets[dev]:
                subnet = self.getsubnet(inet)
                if type(subnet) == int:
                    return ('err', subnet)
                try:
                    ans, unans = arping(subnet, verbose=0)
                except socket.error, e:
                    (etype, evalue, etrace) = sys.exc_info()
                    (errno, err_msg) = evalue
                    return (errno, err_msg)
                #ans是一个队列，每个队列元素是（发送的数据包，收到的回复包）形式的元组
                if len(ans) > 0:
                    for s, r in ans:
                        #收到的包是ether包，arp信息在payload属性中
                        devnbr['nbrs'].append({'ip': r.payload.psrc, 'mac': r.src})
            if devnbr['nbrs'] != []:  #过滤掉没有搜索到邻居的接口
                devnbrs.append(devnbr)
        return devnbrs

    def isnbr(self, sip, dev, dip):
        '''通过arp判断主机在某一接口上与目的ip的联通性
        Args:
            dev: 本主机始发接口
            dip: 目的主机ip
        Returns:
            1: 联通
            0: 不联通
            -1: 发送错误无法判断
        '''
        r_net = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)' +\
                r'/([0-9]|([1-2][0-9])|(3[0-2]))$'
        if re.match(r_net, sip) is not None:
            sip = sip.split('/')[0]
        if re.match(r_net, dip) is not None:
            dip = dip.split('/')[0]
        print('in isnbr:\nsource:%s\nsrc dev:%s\ndestination:%s' % (sip, dev, dip))
        if self.local is None:
            self.islocal()
        if self.local:
            try:
                ans, unans = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(psrc=sip, pdst=dip), verbose=0,
                                 filter='arp and arp[7] = 2', iface=dev, timeout=2)
            except socket.error, e:
                (etype, evalue, etrace) = sys.exc_info()
                (errno, err_msg) = evalue
                if errno == 19:
                    return 0
            if len(ans) == 1:
                (s, r) = ans
                if r.payload.psrc == dip:
                    return 1
            return 0
        ssh = ssh_tools.SshConnect(self.ip, self.uname, self.passwd)
        if ssh.sftp('./remote_arping.py', '/tmp/remote_arping.py') != 0:
            return -1
        lines = ssh.get_cmd_ret('cd /tmp && python remote_arping.py %s %s %s 2>/dev/null' % 
                                (sip, dev, dip))
        if type(lines) == int:
                return lines
        ssh.send_cmd('rm -f /tmp/remote_arping.py')
        print lines
        if lines != [] and lines[0] == '1':
            return 1
        return 0

    


    def probe(self):
        pass
    

if __name__ == '__main__':
    #np = NetProbe('10.32.19.92', 'root', 'sysqa@ftqa')
    np = NetProbe('10.32.19.93', 'root', 'nsiqa')
    #np = NetProbe('10.32.19.92', 'wangbin', 'ljfl2zql')
    #print np.getnets()
    #print np.scanbrs()
    #print np.getsubnet('192.168.15.99/16')
    #np.belongto('10.32.15.34', '10.32.15.0/24')
    #print np.mask2int("255.255.255.0")
    #ans, unans = arping('192.168.30.0/24', verbose=0)
    #for s, r in ans:
    #    print r.payload.psrc, r.src
    #src = "122.32.19.199"
    #net = "10.32.19.93"
    #ans, unans = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(psrc=src, pdst=net), verbose=0,
    #                 filter='arp and arp[7] = 2', iface='br100', timeout=2)
    #ans.summary(lambda (s,r) : r.sprintf('%Ether.src% %ARP.psrc%'))
    #ans, unans = arping("192.168.30.0/28", verbose=0)
    #print NetProbe.samenet('10.32.19.99/24', '10.32.0.0/16')
    print np.isnbr('10.32.19.93/24', 'eth0', '10.32.19.92/24')
    
