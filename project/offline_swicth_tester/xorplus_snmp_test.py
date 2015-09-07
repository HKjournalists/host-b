# -*- coding: utf8 -*-
#!/usr/bin/env python

import subprocess
import shlex
import os
import sys


def gather(ip, oid):
    cmd = 'snmpwalk -c public -v 2c ' + ip + ' ' + oid
    p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    #out = out.strip()
    #print(len(out.split('\n')))
    #index = 0
    #print repr(out)
    #for i in out.split('\n'):
    #    print('%d : %s' % (index + 1, i))
    #    index += 1
    #print('out : %s' % (out))
    #print('err : %s' % (err))
    #print err.strip() == ''
    #return (out.strip(), err.strip())    
    return out.strip()


namelist = ['系统名称', '启动时间', '系统描述', '端口描述', '端口名称', '获取端口速度',
            '端口状态', '端口所配置IP的Mask', '端口进流量', '端口出流量', '端口进error包',
            '端口出error包', '端口收光率', '端口发光率', '等价路由表', '等价路由表的metric值',
            '等价路由表协议类型', 'Ospf对应Ip', 'Ospf对应Area', 'Ospf的Cost', 'Ospf的Router Id',
            '设备ARP表', '设备MAC地址表', '设备温度', 'CPU利用率', 'VLAN名称', 'VLAN所包含的端口',
            'Vlan-interface的Ip', 'Vlan-interface的掩码']

oidlist = [
'1.3.6.1.2.1.1.5',
'1.3.6.1.2.1.1.3',
'1.3.6.1.2.1.1.1',
'1.3.6.1.2.1.2.2.1.2',
'1.3.6.1.2.1.31.1.1.1.18',
'1.3.6.1.2.1.31.1.1.1.15',
'1.3.6.1.2.1.2.2.1.8',
'1.3.6.1.2.1.4.20.1.3',
'1.3.6.1.2.1.2.2.1.10',
'1.3.6.1.2.1.2.2.1.16',
'1.3.6.1.2.1.2.2.1.14',
'1.3.6.1.2.1.2.2.1.20',
'1.3.6.1.4.1.32353.1.6.1.8',
'1.3.6.1.4.1.32353.1.6.1.7',
'1.3.6.1.2.1.4.24.4.1.1',
'1.3.6.1.2.1.4.24.4.1.11',
'1.3.6.1.2.1.4.24.4.1.7',
'1.3.6.1.2.1.14.7.1.1',
'1.3.6.1.2.1.14.7.1.3',
'1.3.6.1.2.1.14.8.1.4',
'1.3.6.1.2.1.14.1.1',
'1.3.6.1.2.1.4.22.1.2',
'1.3.6.1.2.1.17.7.1.2.2.1.2',
'1.3.6.1.4.1.32353.1.5',
'1.3.6.1.4.1.32353.1.1',
'1.3.6.1.2.1.17.7.1.4.3.1.1',
'1.3.6.1.2.1.17.7.1.4.3.1.2',
'1.3.6.1.2.1.4.20.1.1',
'1.3.6.1.2.1.4.20.1.3',
]

ip = sys.argv[1]
outfile = ip + '.txt'

f = open(outfile, 'w')
for i in range(len(oidlist)):
    f.write(namelist[i] + os.linesep)
    f.write(gather(ip, oidlist[i]).strip() + os.linesep)
f.close()
