# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'wangbin19'

SUCCESS = 0
ERROR = -1

ADMIN_INFO_MISSING = -200
ADMIN_INFO_ERROR = -201
IP_FORMAT_ERROR = -202
IP_UNAME_NULL = -203
IP_PSWD_NULL = -204
PARAM_EMPTY = -205

SERVER_IP_EXISTS = -300  	#要配置的ip在服务器上已存在
SERVER_IPFORMAT_ERR = -301  #传入后台的ip字段错误
SERVER_DEV_ERR = -302       #传入后台的dev字段错误
SERVER_SETIP_ERR = -303     #配置ip过程中出错
SERVER_SESTATIC_ERR = -304  #配置静态路由时出错


SWITCH_ADMIN_ERR = -900   
SWITCH_LOGIN_ERR = -901
SWITCH_COMMIT_ERR = -902
SWITCH_SET_ERR = -903

SWITCH_PORTUP_ERR = -911
SWITCH_CREATEVLAN_ERR = -904
SWITCH_SETPORTVLAN_ERR = -905
SWITCH_SETVLANIF_ERR = -906
SWITCH_SETIP_ERR = -908

SWITCH_STATIC_DESTIP_ERR = -912
SWITCH_SETSTATIC_ERR = -913

SERVER_IF_IP_EXISTS = 'ip a | grep -q %s'
SERVER_IF_DEV_EXISTS = 'ip l | grep -q %s'
SERVER_IF_DEV_UP = 'ip l | grep "%s: <.*UP.*>"'
SERVER_IF_DEV_DOWN = 'ip l | grep "%s: <.*UP.*>"'
SERVER_DEV_UP = 'ip l set dev %s up'
SERVER_DEV_DOWN = 'ip l set dev %s down'
SERVER_IP_ADD = 'ip a add %s broadcast + dev %s'
SERVER_IP_DEL = 'ip a del %s broadcast + dev %s'
SERVER_SROUTE_ADD_NOVIA = 'ip r add %s dev %s'
SERVER_SROUTE_DEL_NOVIA = 'ip r del %s dev %s'
SERVER_SROUTE_ADD_VIA = 'ip r add %s via %s'
SERVER_SROUTE_DEL_VIA = 'ip r del %s via %s'


SWITCH_UP_PORT = 'set interface gigabit-ethernet te-1/1/%s disable false'
SWITCH_SHOW_VLAN = 'run show vlans vlan-id %s'
SWITCH_ADD_VLAN = 'set vlans vlan-id %s'
SWITCH_SET_PORT_VLAN = 'set interface gigabit-ethernet te-1/1/%s\
 family ethernet-switching native-vlan-id %s'
SWITCH_SET_PORT_TRUNK = 'set interface gigabit-ethernet te-1/1/%s\
 family ethernet-switching port-mode trunk'
SWITCH_SET_PORT_VMEMBERS = 'set interface gigabit-ethernet te-1/1/%s\
 family ethernet-switching vlan members %s'
SWITCH_SET_RE = r'\[edit\]\s+.*#'
SWITCH_COMMIT_RE = r'Commit OK\.\s+\[edit\]\s+.*#'
SWITCH_COMMIT_TRUNK_RE = r'.*doesn\'t exist\s+\[edit\]\s+.*#'
SWITCH_L3IF_EXISTS = 'run show vlan-interface %s'
SWITCH_ADD_L3IF = 'set vlans vlan-id %s l3-interface %s'
SWITCH_L3IFERR_RE = r'\[.*has been set.*\]'

SWITCH_ADD_IP = 'set vlan-interface interface %s address %s prefix-length %s'
SWITCH_ADD_STATIC = 'set protocols static route %s/%s next-hop %s'

SWITCH_VMEMBERS_EMPTY = 'Vlan Members为空， 请以Vlan ID+空格的形式输入\n例如：11 12 13 14'
SWITCH_VMEMBERS_ERR = 'Vlan Members格式错误，请以Vlan ID+空格的形式输入\n例如：11 12 13 14'