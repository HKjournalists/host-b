# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'wangbin19'

import os
import sys
import subprocess
import json
import re
import telnetlib
import argparse
# 新增
import struct
import socket

import logger
import netprobe
import ssh_tools
import telnet_tools 
import common
import history

class DevManager(object):
    def __init__(self):
        self.basepath = os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep
        self.logger = logger.Logger(self.basepath + 'log')
        self.data = None
        self.svundolist = []
        self.swundolist = []
        self.telobj = None
        #self.ssh = None

    def param_review(self):
        '''检查收到的数据，剔除含有'N/A'的元素，若adminInfo中出现空值则直接报错
           若其他设备信息中出现空值，将该条信息删除（可能是前端页面默认显示的第一条属性，
           而用户提交时没有填写该项）
        Args:
            无
        Returns:
            common.SUCCESS: 通过检测
            common.IP_FORMAT_ERROR: IP格式错误
            common.IP_UNAME_NULL: 用户名为空
            common.IP_PSWD_NULL: 密码为空
        '''
        #print '%sjson data%s\n%s\n%s' % ('='*5, '='*5, str(self.data), '='*20)
        for devtype in self.data:   #data中的顶级对象：Switch或Server
            #print 'now exam main object: ' + devtype  
            for dev in self.data[devtype]:   #遍历Swicth/Server中的每一台设备
                for info in dev:  #遍历每台设备中的各项信息（管理信息/l2/l3/route）
                    #print 'now exam object\'s attribute: ' + info
                    #if type(dev[info]) == dict:
                    if info == 'adminInfo':
                        ret = self.iup_review(dev[info]['ip'], dev[info]['userName'],
                                              dev[info]['passwd'])
                        if ret != common.SUCCESS:
                            return ret
                    elif info == 'l2Interface':
                        self.param_filter(dev[info], ['vtype', 'vmembers'])
                    elif info == 'l3Interface':
                        self.param_filter(dev[info])
                    elif info == 'swStaticRoute':
                        self.param_filter(dev[info])
                    elif info == 'svInterface':
                        self.param_filter(dev[info])
                    elif info == 'svStaticRoute':
                        self.param_filter(dev[info])
        return common.SUCCESS

    def iup_review(self, ip, uname, passwd):
        '''检查ip/username/password（查询信息时使用）
        Args:
        Returns:
            common.SUCCESS: 通过检测
            common.IP_FORMAT_ERROR: IP格式错误
            common.IP_NULL: 
            common.IP_UNAME_NULL: 用户名为空
            common.IP_PSWD_NULL: 密码为空
        '''
        if ip is None or ip == '':
            print json.dumps({'err': 'ip is null!'})
            return common.IP_NULL
        regex = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'
        pattern = re.compile(regex)
        m = pattern.match(ip)
        if m is None:
            print json.dumps({'err': 'ip error!'})
            return common.IP_FORMAT_ERROR
        if uname is None or uname == '':
            print json.dumps({'err': 'need user name!'})
            return common.UNAME_NULL 
        if passwd is None or passwd == '':
            print json.dumps({'err': 'need pass word!'})
            return common.PSWD_NULL
        return common.SUCCESS

    def vmembers_review(self, members):
        '''检查vlan members输入格式
        Args:
            members: 从前端读取的vlan members数据（字符串形式）
        Returns:
            common.SUCCESS: 通过检测
            common.SWITCH_VMEMBERS_EMPTY: 没有输入
            common.SWITCH_VMEMBERS_ERR: 输入格式错误
        '''
        members = members.strip()
        if members.strip() == '':
            return (common.ERROR, common.SWITCH_VMEMBERS_EMPTY)
        members = members.split(' ')
        for i in members:
            if re.match(r'^\d+$', i) is None:
                return (common.ERROR, common.SWITCH_VMEMBERS_ERR)
        return (common.SUCCESS, members)

    def param_filter(self, list, innocent=[]):
        '''属性过滤，若list中的字典对象包含value为空的值，则将其从list中删除
        Args:
            list: 待过滤的列表，其中每个元素都是一个字典对象，如{'name': 'a', 'password': '123'}
            innocent: 豁免列表，若字典对象中的某个key在innocent中，则过滤处理中将其忽略
        Returns:
            无
        '''
        dellist = []
        for element in list:
            for attrname in element:
                if len(innocent) == 0 or attrname not in innocent:
                    value = element[attrname]
                    if value is None or value == '':
                        dellist.append(element)
                        break
        for element in dellist:
            list.remove(element)

    def set_server_info(self, servers):
        '''配置服务器信息
        Args:
            servers: 服务器列表
        Returns:
            common.SUCCESS: 正常执行
            其他返回值参考set_server_ip和set_server_static
        '''
        for server in servers:
            #print type(server['adminInfo'])
            sip = server['adminInfo']['ip']
            sname = server['adminInfo']['userName']
            spasswd = server['adminInfo']['passwd']
            his = history.History(sip, sname, spasswd)
            self.svundolist.append(his)
            #print '%s %s %s' % (sip, sname, spasswd)
            ssh = ssh_tools.SshConnect(sip, sname, spasswd)
            for iface in server['svInterface']:
                ip = iface['ip'] + '/' + iface['mask']
                dev = iface['ifName']
                ret = self.set_server_ip(ssh, ip, dev, his)
                if ret != '0': #shell返回值为字符串，0表示执行成功
                    self.undo(his)
                    return ret
            for static in server['svStaticRoute']:
                destip = '.'.join(static['destIp'].split('.')[:3]) + '.0/' + static['mask']
                via = static['nextIp']
                dev = static['iface']
                #print 'ip:%s  via:%s  dev:%s' % (destip, via, dev)
                ret = self.set_server_static(ssh, destip, via, dev, his)
                if ret != '0':
                    self.undo(his)
                    return ret
        return common.SUCCESS

    def set_server_ip(self, ssh, ip, dev, history):
        '''配置服务器网卡ip
        Args:
            ssh: ssh连接对象
            ip: 网卡ip
            dev: 网卡名
            history: 历史记录，用于恢复
        Returns:
            common.SUCCESS: 正常执行
            common.SERVER_IP_EXISTS: 设定的ip与服务器现有ip冲突
            common.SERVER_DEV_ERR: 设备名出错
        '''
        if re.match(r'.+/$', ip) or re.match(r'.*/$', ip):
            return common.SERVER_IPFORMAT_ERR
        if dev == '' or ssh.send_cmd(common.SERVER_IF_DEV_EXISTS % dev) != '0':
            return common.SERVER_DEV_ERR
        #确认要配置的ip与目标主机现有ip不冲突(返回0为发现冲突)
        if ssh.send_cmd(common.SERVER_IF_IP_EXISTS % ip) == '1':   
            #网卡是否启动(返回0为已经启动)   
            if ssh.send_cmd(common.SERVER_IF_DEV_UP % dev) == '1':     
                ret = ssh.send_cmd(common.SERVER_DEV_UP % dev)
                if ret == '0':
                    #加入history，未来进行还原操作 
                    history.add(common.SERVER_DEV_DOWN % dev)           
            ret = ssh.send_cmd(common.SERVER_IP_ADD % (ip, dev))
            if ret == '0':
                history.add(common.SERVER_IP_DEL % (ip, dev))
            return ret
        else:
            return common.SERVER_IP_EXISTS

    def set_server_static(self, ssh, ip, via, dev, history):
        '''配置服务器静态路由
        Args:
            ssh: ssh连接对象
            ip: 目的ip
            dev: 转发网卡
            via: 下一跳
            history: 历史记录，用于恢复
        Returns:
            0: 成功
            2: 下一跳ip不存在
        '''
        if re.match(r'.+/$', ip) or re.match(r'.*/$', ip):
            return common.SERVER_IPFORMAT_ERR
        if via == '':
            if dev == '':
                return common.SERVER_DEV_ERR
            ret = ssh.send_cmd(common.SERVER_SROUTE_ADD_NOVIA % (ip, dev))
            if ret == '0':
                history.add(common.SERVER_SROUTE_DEL_NOVIA % (ip, dev))
        else:
            ret = ssh.send_cmd(common.SERVER_SROUTE_ADD_VIA % (ip, via))
            if ret == '0':
                history.add(common.SERVER_SROUTE_DEL_VIA % (ip, via))
        return ret

    def set_switch_info(self, switches):
        '''配置交换机信息
        Args:
            servers: 交换机列表
        Returns:
            common.SUCCESS: 正常执行
            common.SWITCH_SET_ERR: 交换机执行set命令时出错
            common.SWITCH_COMMIT_ERR: 执行commit出错
        '''
        # TODO: 1.交换机命令执行部分代码大量冗余，应抽象出一到两个层次进行封装-[已完成-20150606]
        #       2.后续需要实现配置回滚功能（20150507）
        #       
        for switch in switches:
            sip = switch['adminInfo']['ip']
            sname = switch['adminInfo']['userName']
            spasswd = switch['adminInfo']['passwd']
            his = history.History(sip, sname, spasswd)
            self.svundolist.append(his)  #暂时没有用到
            self.telobj = telnet_tools.TelnetXorplus(sip, sname, spasswd)
            for l2if in switch['l2Interface']:
                port = l2if['port']
                pvid = l2if['vlanId']
                vtype = l2if['vtype']
                vmembers = l2if['vmembers']
                if vtype == 1:
                    ret = self.set_switch_l2_trunk(port, pvid, vmembers)
                else:
                    ret = self.set_switch_l2(port, pvid)
                if ret[0] != 0:
                    print json.dumps({'err': ret[1]})
                    return common.ERROR

            for l3if in switch['l3Interface']:
                ifname = l3if['ifName']
                vid = l3if['vlanId']
                ip = l3if['ip']
                mask = l3if['mask']
                ret = self.set_switch_l3(ifname, vid, ip, mask)
                if ret[0] != 0:
                    print json.dumps({'err': ret[1]})
                    return common.ERROR

            for static in switch['swStaticRoute']:
                #'.'.join(static['destIp'].split('.')[:3]) + '.0'
                ip = static['destIp']
                mask = static['mask']
                next = static['nextIp']
                #设置静态路由
                ret = self.set_switch_SR(ip, mask, next)
                if ret[0] != 0:
                    print json.dumps({'err': ret[1]})
                    return common.ERROR
            print json.dumps({'msg': 'set info success'})
            return common.SUCCESS

    def set_switch_l2(self, port, pvid): 
        '''配置交换机vlan信息（access口）
        Args:
            port: 待配置端口
            pvid: 端口的native vlan id
        Returns:
            common.SUCCESS: 正常执行
            common.SWITCH_PORTUP_ERR: up端口失败
            common.SWITCH_CREATEVLAN_ERR: 创建vlan出错
            common.SWITCH_SETPORTVLAN_ERR: 设置端口vlan出错
        '''
        tel = self.telobj
        cmd = common.SWITCH_UP_PORT % (port)     #端口up
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_PORTUP_ERR, 'command fialed: %s' % (cmd))
        cmd = common.SWITCH_SHOW_VLAN % (pvid)   #若vlan不存在则建立该vlan
        ret = tel.send_nocommit(cmd, [r'syntax error, expecting.*']) 
        if ret == 0:
            cmd = common.SWITCH_ADD_VLAN % (pvid)
            ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
            if ret != 0:
                return (common.SWITCH_CREATEVLAN_ERR, 'command fialed: %s' % (cmd))
        cmd = common.SWITCH_SET_PORT_VLAN % (port, pvid)   #设置native vlan id
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETPORTVLAN_ERR, 'command fialed: %s' % (cmd))
        return (common.SUCCESS, 'success')

    def set_switch_l2_trunk(self, port, pvid, members=''):
        '''配置交换机vlan信息（trunk口）
        Args:
            port: 待配置端口
            pvid: 端口的native vlan id
            members: 端口的vlan members列表
        Returns:
            common.SUCCESS: 正常执行
            common.SWITCH_PORTUP_ERR: up端口失败
            common.SWITCH_CREATEVLAN_ERR: 创建vlan出错
            common.SWITCH_SETPORTVLAN_ERR: 设置端口vlan出错
        '''
        vms = self.vmembers_review(members)  #vlan members
        if vms[0] != 0:
            return (common.ERROR, vms[1])
        tel = self.telobj
        cmd = common.SWITCH_UP_PORT % (port)     #端口up
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_PORTUP_ERR, 'command fialed: %s' % (cmd))
        cmd = common.SWITCH_SHOW_VLAN % (pvid)   #若vlan不存在则建立该vlan
        ret = tel.send_nocommit(cmd, [r'syntax error, expecting.*']) 
        if ret == 0:
            cmd = common.SWITCH_ADD_VLAN % (pvid)
            ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
            if ret != 0:
                return (common.SWITCH_CREATEVLAN_ERR, 'command fialed: %s' % (cmd))
        cmd = common.SWITCH_SET_PORT_VLAN % (port, pvid)   #设置native vlan id
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETPORTVLAN_ERR, 'command fialed: %s' % (cmd))
        cmd = common.SWITCH_SET_PORT_TRUNK % (port)  #设置port mode为trunk
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETPORTVLAN_ERR, 'command fialed: %s' % (cmd))
        for i in vms[1]:   #遍历vlan members列表
            cmd = common.SWITCH_SET_PORT_VMEMBERS % (port, i)
            ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], 
                                       [common.SWITCH_COMMIT_RE, common.SWITCH_COMMIT_TRUNK_RE])
            if ret == 1:  #vlan members中的vlan id在交换机中不存在
                return (common.SWITCH_SETPORTVLAN_ERR, 
                        'command fialed: %s\nCan\'t find vlan id %s' % (cmd, i))
            elif ret != 0:
                return (common.SWITCH_SETPORTVLAN_ERR, 'command fialed: %s' % (cmd))
        return (common.SUCCESS, 'success')

    def set_switch_l3(self, ifname, vid, ip, mask):
        '''配置交换机vlan interface信息
        Args:
            ifname: vlan interface名
            vid: vlan interface对应的vlan的id
            ip: vlan interface的ip
            mask: 掩码
        Returns:
            common.SUCCESS: 正常执行
            common.SWITCH_SETVLANIF_ERR: 创建l3接口失败
            common.SWITCH_SETIP_ERR: 创建ip出错
        '''
        #创建l3 interface（重复创建不会影响该端口）
        cmd = common.SWITCH_ADD_L3IF % (vid, ifname)  
        tel = self.telobj
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETVLANIF_ERR, 'command fialed: %s' % (cmd))

        cmd = common.SWITCH_ADD_IP % (ifname, ip, mask)  #设置ip
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETIP_ERR, 'command fialed: %s' % (cmd))        
        return (common.SUCCESS, 'success')

    def set_switch_SR(self, ip, mask, next):
        '''配置交换机静态路由信息
        Args:
            ifname: vlan interface名
            ip: 目的ip
            mask: 掩码
            next: 下一跳
        Returns:
            common.SUCCESS: 正常执行
            common.SWITCH_SETSTATIC_ERR: 创建静态路由失败
        '''
        tel = self.telobj
        cmd = common.SWITCH_ADD_STATIC % (ip, mask, next)  
        ret = tel.send_commit(cmd, [common.SWITCH_SET_RE], [common.SWITCH_COMMIT_RE])
        if ret != 0:
            return (common.SWITCH_SETSTATIC_ERR, 'command fialed: %s' % (cmd))
        return (common.SUCCESS, 'success')

    def get_sw_l2(self):
        '''查询交换机vlan信息，首先通过命令获取信息，然后进行格式解析
        Args:
            无
        Returns:
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
        '''
        vlans = []
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        tel = telnet_tools.TelnetXorplus(ip, username, password)
        lines = tel.get_info_list('run show vlans | no-more')
        if type(lines) != list and lines in [-1, -2, -3, -4, -5]:
            print json.dumps({'err': lines})
            return lines
        i = 4
        #line = Dispatcher.trimline(lines[i])
        line = lines[i].split()
        while i < len(lines) - 1:
            #print line
            vlan = {'id': 0, 'trunk': [], 'access': []}  
            #if re.match(r'\d+', line[0]) is not None:  #匹配到vlan id
            vlan['id'] = line[0]
            del line[0]
            while line[0] != 'untagged':  #读取trunk
                #print line
                for str in line:
                    if re.match(r'(t|q|a)e(-1/1/)?\d\d?\,$', str) is not None:  #匹配端口
                        vlan['trunk'].append(str.replace(',',''))
                i += 1
                line = lines[i].split()
            while (re.match(r'\d+', line[0]) is None) and (i < len(lines) - 1):  #读取access
                #print line
                for str in line:
                    if re.match(r'(t|q|a)e(-1/1/)?\d\d?\,$', str) is not None:
                        #print str
                        vlan['access'].append(str.replace(',',''))
                while True:    #run show vlan输出的信息中vlan之间有时会出现空行，需要跳过
                    i += 1
                    line = lines[i].split()
                    if len(line) != 0:
                        break

            vlans.append(vlan)       
        print json.dumps(vlans)   #将json对象转化为json字符串，打印给node.js后台 

    def get_sw_l3(self):
        '''查询交换机vlan-interface信息
        Args:
            无
        Returns:
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
        '''
        vifs = []
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        tel = telnet_tools.TelnetXorplus(ip, username, password)
        lines = tel.get_info_list('run show vlan-interface | no-more')
        if type(lines) != list and lines in [-1, -2, -3, -4, -5]:
            print json.dumps({'err': lines})
            return lines    
        i = 2
        line = lines[i].split()
        while i < len(lines) - 1:
            vif = {'vifId': '0', 'state': '0', 'vid': '0', 'addrs': []} 
            if 'Hwaddr' in line:  
                vif['vifId'] = line[0]
                vif['vid'] = line[3].split(':')[1][:-1]
                vif['state'] = line[len(line) - 1].split(':')[1]
                vif['addrs'].append(lines[i+1].split()[2])
                i += 2
                line = lines[i].split()
                while len(line) == 1 and line[0].find('/') != -1:  #读取ip
                    vif['addrs'].append(line[0])
                    i += 1
                    line = lines[i].split()
                vifs.append(vif)
            i += 1
            line = lines[i].split()
        print json.dumps(vifs)   #将json对象转化为json字符串，打印给node.js后台 

    def get_sw_sr(self):
        '''查询交换机static route信息
        Args:
            无
        Returns:
            -1: 登陆过程中出错
            -2: 交换机要求输入用户名、密码但用户名/密码为空
            -3: socket error 无法建立telnet连接
            -4: 连接异常终止
            -5: 传入的cmd包含'\n'
        '''
        routes = []
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        tel = telnet_tools.TelnetXorplus(ip, username, password)
        #run show route forward-route ipv4 all
        lines = tel.get_info_list('run show route table ipv4 unicast final terse | no-more')
        if type(lines) != list and lines in [-1, -2, -3, -4, -5]:
            print json.dumps({'err': lines})
            return lines   
        i = 3
        while i < len(lines) - 1:
            route = {'dest': '0', 'mask': '0', 'next': '0'} 
            line = lines[i].split()
            route['dest'] = line[0].split('/')[0]
            route['mask'] = line[0].split('/')[1]
            route['next'] = line[4].split('/')[0]
            routes.append(route)
            i += 1
        print json.dumps(routes)   #将json对象转化为json字符串，打印给node.js后台

    def get_sv_if(self):
        '''查询服务器网卡信息
        Args:
            无
        Returns:
            -1: 连接服务器出错
            -2: socket超时
        '''
        ifs = []
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        ssh = ssh_tools.SshConnect(ip, username, password)
        lines = ssh.get_cmd_ret('ip a')
        if type(lines) == int:
            print json.dumps({'err': lines})
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
        print json.dumps(ifs)    #将json对象转化为json字符串，打印给node.js后台

    def get_sv_sr(self):
        '''查询服务器路由信息
        Args:
            无
        Returns:
            -1: 连接服务器出错
            -2: socket超时
        '''
        routes = []
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        ssh = ssh_tools.SshConnect(ip, username, password)
        lines = ssh.get_cmd_ret('route -n')
        #if type(lines) != list and lines in [-1, -2, -3]:
        if type(lines) == int:
            print json.dumps({'err': lines})
            return lines   
        i = 2
        while i < len(lines):
            route = {'dest': '0', 'gw': '0', 'mask': '0', 'metric': '0', 'iface': '0'}
            line = lines[i].split()
            route['dest'] = line[0]
            route['gw'] = line[1]
            route['mask'] = line[2]
            route['metric'] = line[4]
            route['iface'] = line[7]
            routes.append(route)
            i += 1
        print json.dumps(routes)   #将json对象转化为json字符串，打印给node.js后台


    def get_connectivity(self):
        '''
        连通性判断
        Args:
            无
        Returns:
            -1: ssh连接出错   
        self.data = {
            'src': {'ip': '10.32.19.211', 'username': 'root', 'password': 'nsi7654321', 'dev': 'sv'},
            'dst': {'ip': '10.32.19.64', 'username': 'root', 'password': 'nsi1234567', 'dev': 'sv'}
        }
        '''
        json_result = {
            'isConnect' : '0',
            'connInfo' : []
        }
        src_ip = self.data['src']['ip']
        src_username = self.data['src']['username']
        src_password = self.data['src']['password']
        src_dev = self.data['src']['dev']
        dst_ip = self.data['dst']['ip']
        dst_username = self.data['dst']['username']
        dst_password = self.data['dst']['password']
        dst_dev = self.data['dst']['dev']

        if (src_dev == 'sv') and (dst_dev == 'sv'):
            # 只提取ping结果的第二行，然后判断是否连通
            # 连通判断依据为返回结果中匹配到time，
            # 如果不通，返回结果匹配到 Destination Host Unreachable
            src_ssh = ssh_tools.SshConnect(src_ip, src_username, src_password)
            dst_ssh = ssh_tools.SshConnect(dst_ip, dst_username, dst_password)
            conn_lines = src_ssh.get_cmd_ret("ping -c 1 10.32.19.64 | sed -n '2,2p'")
            if type(conn_lines) == int:  #ssh连接异常
                #print json.dumps({'err': 'ssh connect error'})
                return -1
            mask = ''
            if conn_lines[0].find('time') > 0:
                json_result['isConnect'] = 1
                cinfo = {
                    'cFlag': 'connected', 
                    'cType': 'full', 
                    'srcInterface': '', 
                    'dstInterface': '',
                    'srcNet': '', 
                    'dstNet': '', 
                    'extra': ''
                }
                # 获取源ip服务器所有接口名
                ifaces = src_ssh.get_cmd_ret("netstat -ni | cut -d ' '  -f 1 | sed -n '3,$p'")
                if type(ifaces) == int:  #ssh连接异常
                    #print json.dumps({'err': 'ssh connect error'})
                    return -1
                for iface in ifaces:
                    iface = iface.replace('\n', '')
                    #print iface
                    if_result = src_ssh.get_cmd_ret("ifconfig {0} | sed -n '2,2p'".format(iface))
                    if if_result[0].find(src_ip) > 0:
                        mask = if_result[0].split('Mask:')[1]
                        #print common.MASK_LEN[mask]
                        cinfo['srcInterface'] = iface
                        break
                # 获取目的ip服务器所有接口名
                ifaces = dst_ssh.get_cmd_ret("netstat -ni | cut -d ' '  -f 1 | sed -n '3,$p'")
                if type(ifaces) == int:  #ssh连接异常
                    #print json.dumps({'err': 'ssh connect error'})
                    return -1
                for iface in ifaces:
                    # 由于获取的接口名中包含\n字符，因此这里需要替换掉
                    iface = iface.replace('\n', '')
                    if_result = dst_ssh.get_cmd_ret("ifconfig {0}".format(iface))
                    if if_result[1].find(dst_ip) > 0:
                        cinfo['dstInterface'] = iface
                        break
                # 获取网络号
                ip = socket.ntohl(struct.unpack("I", socket.inet_aton(str(src_ip)))[0])
                int_mask = socket.ntohl(struct.unpack("I", socket.inet_aton(str(mask)))[0])
                network = socket.inet_ntoa(struct.pack('I', socket.htonl(ip & int_mask)))
                cinfo['srcNet'] = network + '/' + common.MASK_LEN[mask]
                cinfo['dstNet'] = network + '/' + common.MASK_LEN[mask]
                json_result['connInfo'].append(cinfo)
            elif conn_lines[0].find('Destination Host Unreachable') > 0:
                json_result['isConnect'] = 0

        elif (src_dev == 'sv') and (dst_dev == 'sw'):
            ''' 待处理
            '''

        elif (src_dev == 'sw') and (dst_dev == 'sv'):
            ''' 待处理
            '''

        elif (src_dev == 'sw') and (dst_dev == 'sw'):
            ''' 待处理
            '''
        print json.dumps(json_result)

    def get_nbrs(self):
        '''
        获取邻居信息
        Args:
            无
        Returns:
            ret: 每个网卡的直连邻居信息，格式为：
                 [{'dev': '接口1', nbrs: [{'ip': '邻居ip', 'mac': '邻居mac'}, ...]}, ...]
            -1: 获取失败  
        '''
        ip = self.data['ip']
        username = self.data['username']
        password = self.data['password']
        np = netprobe.NetProbe(ip, username, password)
        ret = np.scanbrs()
        if type(ret) == tuple:
            print json.dumps({'err': 'get neighbors failed: ' + ret[1]})
            return -1
        print json.dumps(ret)

    def get_connectivity2(self):
        self.data = {
            'src': {'ip': '10.32.19.93', 'username': 'root', 'password': 'nsiqa', 'dev': 'sv'},
            'dst': {'ip': '10.32.19.99', 'username': 'root', 'password': 'nsi7654321', 'dev': 'sv'}
        }
        json_result = {
            'isConnect' : 0,
            'connInfo' : []
        }
        src_ip = self.data['src']['ip']
        src_username = self.data['src']['username']
        src_password = self.data['src']['password']
        #src_dev = self.data['src']['dev']
        dst_ip = self.data['dst']['ip']
        dst_username = self.data['dst']['username']
        dst_password = self.data['dst']['password']
        #dst_dev = self.data['dst']['dev']  
        nps = netprobe.NetProbe(src_ip, src_username, src_password)
        npd = netprobe.NetProbe(dst_ip, dst_username, dst_password)
        flag = 0
        mngip = '10.32.0.0/16'
        src_devs = nps.getnets()
        dst_devs = npd.getnets()
        print(src_devs)
        print(dst_devs)
        for sdev in src_devs:    #TODO 循环待改进
            if sdev == 'lo':
                continue
            #print('sdev: ' + sdev)
            for ddev in dst_devs:
                if ddev == 'lo':
                    continue
                #print('ddev: ' + ddev)
                for sip in src_devs[sdev]:
                    #print('sip: ' + sip)
                    ret = netprobe.NetProbe.samenet(sip, mngip)
                    if ret == -1 or ret:
                        continue
                    for dip in dst_devs[ddev]:
                        #print('dip: ' + dip)
                        ret = netprobe.NetProbe.samenet(dip, mngip)
                        if ret == -1 or ret:
                            continue
                        if netprobe.NetProbe.samenet(sip, dip):
                            if nps.isnbr(sip.split('/')[0], sdev, dip.split('/')[0]) == 1:
                                if flag == 0:
                                    flag = 1
                                if json_result['isConnect'] == 0:
                                    json_result['isConnect'] = 1
                                cinfo = {
                                    'cFlag': 'connected', 'cType': 'full', 
                                    'srcInterface': sdev, 'dstInterface': ddev,
                                    'srcNet': sip, 'dstNet': dip, 'extra': ''
                                }
                                json_result['connInfo'].append(cinfo)
        if flag == 1:
            print json.dumps(json_result)
            return 0   
        #print('########################')
        for sdev in src_devs:            #TODO 同上
            if sdev == 'lo':
                continue
            #print('sdev: ' + sdev)
            for ddev in dst_devs:
                if ddev == 'lo':
                    continue
                #print('ddev: ' + ddev)
                for sip in src_devs[sdev]:
                    #print('sip: ' + sip)
                    ret = netprobe.NetProbe.samenet(sip, mngip)
                    #print(ret)
                    if ret == -1 or ret:
                        continue
                    for dip in dst_devs[ddev]:
                        #print('dip: ' + dip)
                        ret = netprobe.NetProbe.samenet(dip, mngip)
                        #print(ret)
                        if ret == -1 or ret:
                            continue
                        src_ssh = ssh_tools.SshConnect(src_ip, src_username, src_password)
                        dst_ssh = ssh_tools.SshConnect(dst_ip, dst_username, dst_password)
                        sip = netprobe.NetProbe.iplus(dip)
                        src_ssh.send_cmd('ip l set dev %s down' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s arp off' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s up' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s arp on' % (sdev))
                        src_ssh.send_cmd('ip a add %s dev %s' % (sip, sdev))
                        dst_ssh.send_cmd('ip l set dev %s down' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s arp off' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s up' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s arp on' % (ddev))
                        if nps.isnbr(sip.split('/')[0], sdev, dip.split('/')[0]) == 1:
                            cinfo = {
                                'cFlag': 'unconnected', 'cType': 'break', 
                                'srcInterface': sdev, 'dstInterface': ddev,
                                'srcNet': 'N/A', 'dstNet': dip, 
                                'extra': 'need to add interface info'
                            }
                            json_result['connInfo'].append(cinfo)
                        src_ssh.send_cmd('ip a del %s dev %s' % (sip, sdev))
                        src_ssh.send_cmd('ip l set dev %s down' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s arp off' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s up' % (sdev))
                        src_ssh.send_cmd('ip l set dev %s arp on' % (sdev))
                        dst_ssh.send_cmd('ip l set dev %s down' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s arp off' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s up' % (ddev))
                        dst_ssh.send_cmd('ip l set dev %s arp on' % (ddev))
        print json.dumps(json_result)
        return 0
                                          

    def undo(self, his=None):
        '''还原服务器操作
        Args:
            his: 还原操作对象
        Returns:
            无
        '''
        templist = []
        if his is not None:
            templist.append(his)
        else:
            templist = self.svundolist
        for i in self.svundolist:
            ssh = ssh_tools.SshConnect(i.ip, i.username, i.passwd)
            for cmd in i.cmdlist:
                print('undo: %s' % (cmd))
                ret = ssh.send_cmd(cmd)
                print('return: %s' % str(ret))

    def undo2(self, his=None):
        '''还原交换机操作
        Args:
            his: 还原操作对象
        Returns:
            无
        '''
        pass

    def run(self): 
        parser = argparse.ArgumentParser(description="Dev Manager")
        parser.add_argument('--set', help = 'set switch/server info', action = 'store_true')
        parser.add_argument('--get-sw', help = 'get switch info', action = 'store_true')
        parser.add_argument('--get-sv', help = 'get server info', action = 'store_true')
        parser.add_argument('--get-conn', help = 'get connectivity info', action = 'store_true')
        parser.add_argument('--get-nbrs', help = 'get neighbors', action = 'store_true')
        parser.add_argument('--L2', help = 'get l2 info', action = 'store_true')
        parser.add_argument('--L3', help = 'get l3 info', action = 'store_true')
        parser.add_argument('--If', help = 'get interface info', action = 'store_true')
        parser.add_argument('--SR', help = 'get static route info', action = 'store_true')
        parser.add_argument('-d', '--data' , dest = 'data' ,help = 'json data from server', 
                            default = None)
        args = parser.parse_args()
        if args.data is None:
            print json.dumps({'err': 'no data!'})
            return  common.ERROR
        self.data = json.loads(args.data)  #将传入的json字符串转化为json对象
        if args.set:
            ret = self.param_review()
            if ret != common.SUCCESS:
                return ret
            if self.data['Server']:
                self.set_server_info(self.data['Server'])
            if self.data['Switch']:
                self.set_switch_info(self.data['Switch'])
        elif args.get_sw:   #注意这里判断匹配--get-sw选项时需要用get_sw
            ret = self.iup_review(self.data['ip'], self.data['username'], self.data['password'])
            if ret != common.SUCCESS:
                return ret
            if args.L2:
                self.get_sw_l2()
            elif args.L3:
                self.get_sw_l3()
            elif args.SR:
                self.get_sw_sr()
        elif args.get_sv:
            ret = self.iup_review(self.data['ip'], self.data['username'], self.data['password'])
            if ret != common.SUCCESS:
                return ret
            if args.If:
                self.get_sv_if()
            elif args.SR:
                self.get_sv_sr()
        elif args.get_conn:
            src = self.data['src']
            dst = self.data['dst']
            ret = self.iup_review(src['ip'], src['username'], src['password'])
            if ret != common.SUCCESS:
                return ret
            ret = self.iup_review(dst['ip'], dst['username'], dst['password'])
            if ret != common.SUCCESS:
                return ret
            self.get_connectivity()  #没有检查devType，因为是直接从设备对象读取而非用户输入
        elif args.get_nbrs:
            ret = self.iup_review(self.data['ip'], self.data['username'], self.data['password'])
            if ret != common.SUCCESS:
                return ret
            self.get_nbrs() 


if __name__ == '__main__':
    m = DevManager()
    #m.get_connectivity()
    #m.run()
    # ifconfig | grep -A1 eth0 | grep inet | awk '{print $2}' | awk 'BEGIN{FS=":"}{print $2}'
    # ip address add 192.168.50.50/24 broadcast + dev eth0 label eth0:1
    m.get_connectivity2()
    '''
    m.data = {
    u'Switch': [
        {
        u'adminInfo': {u'userName': u'aaa', u'ip': u'1.1.1.1', u'devName': u'Switch0', 
                       u'passwd': u'aa'}, 
        u'l2Interface': [{u'opPort': u'', u'port': u'1', u'vlanId': u'2'}], 
        u'l3Interface': [{u'ip': u'', u'ifName': u'', u'mask': u'', u'vlanId': u''}], 
        u'swStaticRoute': [{u'destIp': u'', u'mask': u'', u'nextIp': u''}]
        }
    ], 
    u'Server': []
    }
    m.param_review()
    print m.data
    '''