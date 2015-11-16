#-*- coding: utf8 -*-
#/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
交换机线上抓包框架
Authors: wangbin19@baidu.com
Date:    2015/10/22 00:06:20
Todo:    
"""

import os
import re
import sys
import time
import Queue
import shlex
import signal
import socket
import struct
import logging
import logging.handlers
import pexpect
import argparse
import threading
import traceback
import subprocess
import ConfigParser
import multiprocessing

import bpu
import pexpect_tools

class XorplusDebugger(object):
    """Xorplus调试器
    Attributes:
        logger: 日志对象
        cfg_file: 配置文件路径
        sw_ip: 交换机管理ip
        sw_user: 交换机管理用户名
        sw_pwd: 交换机管理密码密码
        sw_shpwd: 交换机shell密码
        sw_rtpwd: 交换机shell的root用户密码
        loc_ip: 本机ip
        loc_user: 本机用户名
        loc_pwd: 本机密码
        loc_lib_path: 本地库文件路径
        symbol_dict: 需要建立的符号链接
    """
    def __init__(self):
        self.logger = MiniLogger('XorplusDebugger', 'xdebug.log').initialize()
        self.cfg_file = None
        self.sw_ip = None
        self.sw_user = None
        self.sw_pwd = None
        self.sw_shpwd = None
        self.sw_rtpwd = None
        self.loc_ip = None
        self.loc_user = None
        self.loc_pwd = None
        self.loc_lib_path = None
        self.symbol_dict = None        

    def parse_arg(self):
        """处理命令行参数
        Args:
            无
        Returns:
            0: 参数正常
            -1: 参数错误
        """
        parser = argparse.ArgumentParser(description='gdb auto test')
        parser.add_argument('-v', action='version', version='v0.2')
        parser.add_argument('-c', dest='conf', help='path of config file', default = None)
        args = parser.parse_args()
        if args.conf is None:
            self.logger.error(u'请使用-c指定配置文件路径')
            return -1
        self.cfg_file = args.conf
        return 0

    def start_debug(self):
        """读取配置文件，分配多线程调试
        Args:
            None
        Returns:
            0: 正常处理
            -1: 配置文件出错
        """
        parser = ConfigParser.ConfigParser()
        self.logger.debug('load config files success')
        try:
            parser.read(self.cfg_file)
            self.sw_ip = parser.get('common', 'ip')
            self.sw_user = parser.get('common', 'username')
            self.sw_pwd = parser.get('common', 'password')
            self.loc_ip = parser.get('common', 'loc_ip')
            self.loc_user = parser.get('common', 'loc_username')
            self.loc_pwd = parser.get('common', 'loc_password')
            self.sw_shpwd = parser.get('common', 'sh_password')
            self.sw_rtpwd = parser.get('common', 'root_password')
            self.loc_lib_path = parser.get('common', 'loc_lib_path')
            self.symbol_dict = parser.get('common', 'symbol_dict')
            parser.remove_section('common')
            sections = parser.sections()      
        except ConfigParser.NoSectionError, e:
            self.logger.error(e)
            return -1
        #ip正则表达式 [01]?\d\d?:0-199、2[0-4]\d:200-249、25[0-5]:250-255
        regex = r'^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$'
        pattern = re.compile(regex)
        m_loc = pattern.match(self.loc_ip)
        m_sw = pattern.match(self.sw_ip)
        if m_loc is None or m_sw is None:
            self.logger.error(u'ip格式错误')
            return -1

        (rm_files, mv_files) = self.prepare()

        threads = {} # 记录创建的所有子进程

        queue = multiprocessing.Queue() # 控制信息传递队列
        ev = multiprocessing.Event() # 退出标记，初始值为False
        #queue = Queue.Queue()
        #ev = threading.Event()

        #收到SIGINT，通知proxy停止读取数据
        signal.signal(signal.SIGINT, lambda x, y: ev.set())
        signal.siginterrupt(signal.SIGINT, False)
        for section in sections:
            try:
                loc_pg_path = parser.get(section, 'loc_pg_path')
                sw_pg_dir = parser.get(section, 'sw_pg_dir')
                loc_src_dir = parser.get(section, 'loc_src_dir')
                sw_src_dir = parser.get(section, 'sw_src_dir')
                gdb_cfg_path = parser.get(section, 'gdb_cfg_path')
                loc_gs_path = parser.get(section, 'loc_gs_path')
            except ConfigParser.NoOptionError, e:
                self.logger.error(e)
                return -1
            if not (loc_pg_path and sw_pg_dir and loc_src_dir and sw_src_dir):
                self.logger.error('found empty option in %s' % (self.cfg_file))
                return -1
            mod = ModuleDebugger(section, queue, ev, self.sw_ip, self.sw_user, self.sw_pwd, 
                                 self.sw_shpwd, self.sw_rtpwd, self.loc_ip, self.loc_user, 
                                 self.loc_pwd, loc_pg_path, sw_pg_dir, loc_src_dir, sw_src_dir,
                                 gdb_cfg_path, loc_gs_path)
            mod.start()

            threads[mod.pid] = mod
            print('thread %s started' % (mod.pid))
            #threads[mod.ident] = mod
            #print('thread %s started' % (mod.ident))

        while True:
            item = queue.get()
            if item['event'] == 'exit':
                t = threads.pop(item['pid'])
                t.join()
                print('thread %s end' % (item['pid']))
            if not threads: # 所有子进程均已退出
                break

        self.recover(rm_files, mv_files) 

        return 0

    def prepare(self):
        """复制全局库文件到交换机
        Args:
            None
        Returns:
            rm_files: 复制到交换机和在交换机上新建的文件列表，调试结束后需删除
            mv_files: 交换机上备份的文件列表，调试结束后需恢复
            -1: 失败
        """
        rm_files = []
        mv_files = []
        sw_lib_dir = '/lib'   #硬编码，交换机库文件目录一般不会变
        con = pexpect_tools.Pexpc4Xorplus(self.sw_ip, self.sw_user, self.sw_pwd, self.sw_shpwd,
                                           self.sw_rtpwd)
        try:
            con.start_sh()
            for path in self.loc_lib_path.split('|'):
                (dir, file) = os.path.split(path.strip())
                #dir = path[: path.rfind('/')].strip()
                #file = path[path.rfind('/') + 1:].strip()
                if con.file_check(sw_lib_dir, file, '.bak') == 1:
                    mv_files.append(os.path.join(sw_lib_dir, file))
                rm_files.append(os.path.join(sw_lib_dir, file))
                con.file_scp('%s:%s' % (self.loc_ip, os.path.join(dir, file)), sw_lib_dir, 
                             self.loc_user, self.loc_pwd)
            for dict in self.symbol_dict.split('|'):
                dst = dict.split('->')[0].strip()
                src = dict.split('->')[1].strip()
                if con.file_check(sw_lib_dir, dst, '.bak') == 1:
                    mv_files.append(os.path.join(sw_lib_dir, dst))
                rm_files.append(os.path.join(sw_lib_dir, dst))
                con.single_cmd('ln -s %s %s' % (src, dst), [r'#'])
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        finally:
            con.close_sh()
        #print rm_files
        #print mv_files
        return (rm_files, mv_files)

    def recover(self, rm_files, mv_files):
        """恢复交换机库文件环境
        Args:
            rm_files: 复制到交换机和在交换机上新建的文件列表，调试结束后需删除
            mv_files: 交换机上备份的文件列表，调试结束后需恢复
        Returns:
            0: 成功
            -1: 失败
        """
        con = pexpect_tools.Pexpc4Xorplus(self.sw_ip, self.sw_user, self.sw_pwd, self.sw_shpwd,
                                           self.sw_rtpwd)
        try:
            con.start_sh()
            for file in rm_files:
                con.single_cmd('rm -f %s' % (file), [r'#'])
            for file in mv_files:
                con.single_cmd('mv %s%s %s' % (file, '.bak', file), [r'#']) 
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        finally:
            con.close_sh()
        return 0

class ModuleDebugger(multiprocessing.Process):   # threading.Thread / multiprocessing.Process
    """模块调试器
    Attributes:
        logger: 日志对象
        name: 模块名
        queue: 消息队列
        ev: 事件对象
        sw_ip: 交换机管理ip
        sw_user: 交换机管理用户名
        sw_pwd: 交换机管理密码密码
        sw_shpwd: 交换机shell密码
        sw_rtpwd: 交换机shell的root用户密码
        loc_ip: 本机ip
        loc_user: 本机用户名
        loc_pwd: 本机密码
        loc_pg_path: 本地Xorplus模块主程序路径（与交换机中模块主程序名相同）
        sw_pg_dir: 交换机Xorplus模块主程序所在目录（符号表、断点文件、gdb脚本同样复制至此目录中）
        loc_src_dir: 本地Xorplus模块源文件所在目录，多个目录用“|”分隔
        sw_src_dir: 交换机Xorplus源文件储存目录（本地源文件复制到交换机的位置）
        gdb_cfg_path: gdb配置文件路径
        loc_gs_path: 本地Xorplus模块调试所需的gdb脚本路径
        con: 连接对象  
        breaks: 断点列表
        vars: 变量列表
    """
    def __init__(self, name, queue, ev, sw_ip, sw_user, sw_pwd, sw_shpwd, sw_rtpwd, 
                 loc_ip, loc_user, loc_pwd, loc_pg_path, sw_pg_dir, loc_src_dir, sw_src_dir, 
                 gdb_cfg_path, loc_gs_path):
        super(self.__class__, self).__init__()
        #signal.signal(signal.SIGINT, self.handler)
        self.logger = MiniLogger(name, '%s.log' % (name)).initialize()
        self.queue = queue
        self.ev = ev
        self.sw_ip = sw_ip.strip()
        self.sw_user = sw_user.strip()
        self.sw_pwd = sw_pwd.strip()
        self.sw_shpwd = sw_shpwd.strip()
        self.sw_rtpwd = sw_rtpwd.strip()
        self.loc_ip = loc_ip.strip()
        self.loc_user = loc_user.strip()
        self.loc_pwd = loc_pwd.strip()
        self.loc_pg_path = loc_pg_path.strip()
        self.sw_pg_dir = sw_pg_dir.strip()
        self.loc_src_dir = loc_src_dir.strip()
        self.sw_src_dir = sw_src_dir.strip()
        self.gdb_cfg_path = gdb_cfg_path.strip()
        self.loc_gs_path = loc_gs_path.strip()
        self.con = pexpect_tools.Pexpc4Xorplus(self.sw_ip, self.sw_user, 
                                               self.sw_pwd, self.sw_shpwd, self.sw_rtpwd)
        self.breaks = []
        self.vars = []

    def run(self):
        """执行调试进程
        Args:
            None
        Returns:
            None
        """
        self.logger.debug('thread start')
        ret = self.prepare()
        if ret == -1:
            self.logger.error('prepare failed')
            return
        ret = self.gen_gs(ret)
        if ret == -1:
            self.logger.error('gen_gs failed')
            return

        #桩，只构建环境不进行自动调试，手动调试时使用
        #self.queue.put({'event': 'exit', 'pid': self.ident})
        #return 0

        self.start_gdb(ret)
        self.logger.debug('thread end')
        
    def prepare(self):
        """复制模块所需的调试信息（符号表，源文件）
        Args:
            None
        Returns:
            rm_paths: 复制到交换机和在交换机上新建的文件或目录，调试结束后需删除
            -1: 失败
        """
        rm_paths = []  #此步骤向交换机复制的文件均为交换机本身没有的文件，不考虑备份的情况
        (dir, file) = os.path.split(self.loc_pg_path.strip())   
        loc_debug_file = '%s/%s.debug' % (dir, file)            
        if not os.path.exists(loc_debug_file):                            #分离符号表
            if not os.path.exists('./strip_debug.sh'):
                self.logger.error('can\'t find %s' % ('strip_debug.sh'))
                return -1
            cmd = 'sh strip_debug.sh %s >/dev/null 2>&1' % (self.loc_pg_path)
            if os.system(cmd) != 0:
                self.logger.error('can\'t sperate debug info from %s' % (self.loc_pg_path))
                return -1
            self.logger.debug('genertate local symbol file: %s' % (loc_debug_file))
        try:
            self.con.start_sh()
            rm_paths.append(os.path.join(self.sw_pg_dir, '%s.debug' % (file)))
            self.con.file_scp('%s:%s' % (self.loc_ip, loc_debug_file), self.sw_pg_dir, 
                         self.loc_user, self.loc_pwd)                      #复制符号表
            self.logger.debug('copy symbol file %s to switch complete' % (loc_debug_file))
            regex = r'^.*\.((cc)|(hh)|(h)|(c))$'
            pattern = re.compile(regex)
            for dir in self.loc_src_dir.split('|'):
                dir = dir.strip()  
                if not os.path.isdir(dir):
                    self.logger.error('invalid src dir %s' % (dir))
                    return -1
                cmd = 'sh scan.sh %s' % (dir)  #扫描本地源文件目录，过滤出.c/.cc/.h/.cc文件
                p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
                out, err = p.communicate()
                if err != '':
                    self.logger.error('scan src dir failed: %s' % (err))
                    return -1
                temp_dir = os.path.join(dir, os.path.split(self.sw_src_dir)[1])
                os.system('sudo mkdir -p %s' % (temp_dir))
                for src_file in out.split():
                    if pattern.match(src_file) is not None:
                        os.system('sudo \cp -f %s %s >/dev/null 2>&1' % (src_file, temp_dir))
                rm_paths.append(self.sw_src_dir)
                self.con.file_scp('%s:%s' % (self.loc_ip, temp_dir), 
                                  self.sw_pg_dir, self.loc_user, self.loc_pwd, True)  #复制源文件
                self.logger.debug('copy src files to switch complete')  
                os.system('sudo rm -rf %s' % (temp_dir))
            return rm_paths
        except AttributeError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            self.recover(rm_paths)
            return -1   
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            self.recover(rm_paths)
            return -1   
        finally:
            self.con.close_sh() 

    def gen_gs(self, rm_paths=[]):
        '''读取gdb配置文件，生成gdb脚本并复制到交换机
        Args:
            rm_paths: 复制到交换机和在交换机上新建的文件或目录，调试结束后需删除
        Returns:
            rm_paths: 同上
            -1: 失败
        '''
        if not os.path.exists(self.gdb_cfg_path):   
            self.logger.error('can\'t find gdb config file in %s' % (self.gdb_cfg_path))
            return -1
        parser = ConfigParser.ConfigParser()
        try:
            parser.read(self.gdb_cfg_path)
            for k, v in parser.items('breaks'):
                self.breaks.append(v)
            for k, v in parser.items('vars'):
                self.vars.append(v)
        except ConfigParser.NoSectionError, e:
            self.logger.error(e)
            return -1
        self.logger.debug('load gdb config file success')
        with open(self.loc_gs_path, 'w+') as fp:
            #交换机源文件目录写入gdb脚本
            fp.write('directory %s\n' % (self.sw_src_dir)) 
            #交换机上的符号表路径
            sw_symbol_path = '%s/%s.debug' % (self.sw_pg_dir, os.path.split(self.loc_pg_path)[1])    
            #符号表路径写入gdb脚本
            fp.write('symbol-file %s\n' % (sw_symbol_path))
            for bp in self.breaks:
                fp.write('b %s\n' % (bp))
        try:
            self.con.start_sh()
            rm_paths.append(os.path.join(self.sw_pg_dir, os.path.split(self.loc_gs_path)[1]))
            self.con.file_scp('%s:%s' % (self.loc_ip, self.loc_gs_path), self.sw_pg_dir, 
                         self.loc_user, self.loc_pwd)           #复制gdb脚本到交换机
            self.logger.debug('copy %s to swich complete' % (self.loc_gs_path))
            return rm_paths
        except AttributeError, e:
            self.logger.error(e) 
            traceback.print_exc(file=sys.stdout)
            self.recover(rm_paths)
            return -1   
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            self.recover(rm_paths)
            return -1
        finally:
            self.con.close_sh() 

    def start_gdb(self, rm_paths=None):
        '''开始gdb调试
           由于使用pexpect调用gdb可能引发的超时问题，本函数中与gdb相关的操作均使用未封装的
           原始pexpect调用，具体信息参考pexpect官方文档中FAQ一章中的 Q: Why not just use Expect?
        Args:
            rm_paths: 复制到交换机和在交换机上新建的文件或目录，调试结束后需删除
        Returns:
            0: 成功
            -1: 失败
        '''
        prompt = r'\n\(gdb\)\W'
        sw_gs_path = os.path.join(self.sw_pg_dir, os.path.split(self.loc_gs_path)[1])
        sw_pg_name = os.path.split(self.loc_pg_path)[1]
        try:
            sh = self.con.start_sh()
            self.con.single_cmd('cd %s' % (self.sw_pg_dir), [r'#'])    #进入模块目录
            pid = self.con.send_echo('pgrep %s' % (sw_pg_name), r'#')[0]    #获取pid
            cmd = 'gdb attach %s' % (pid)
            sh.sendline(cmd)                                                #进入gdb
            index = sh.expect([cmd, pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print sh.before.replace('\x00', '').strip()   #读取到的字符中含有\x00，why?
                print sh.after.replace('\x00', '').strip()
            index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 5)
            if index == 0:
                print sh.before.replace('\x00', '').strip()
                print sh.after.replace('\x00', '').strip()
            #ret = self.con.single_cmd('source %s' % (sw_gs_path), [r'\(y or n\)', prompt], None)
            #print self.con.expsh.before.replace('\x00', '').strip()
            #if ret == 0:
            #    ret = self.con.send_echo('y', prompt)
            cmd = 'source %s' % (sw_gs_path)
            sh.sendline(cmd)
            index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 5)
            if index == 0:
                print sh.before.replace('\x00', '').strip()
                print sh.after.replace('\x00', '').strip()
            while not self.ev.is_set():
                bidx = None
                sh.sendline('continue')
                index =sh.expect(['continue', pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    print sh.before.replace('\x00', '').strip()
                    print sh.after.replace('\x00', '').strip()
                index = sh.expect(['Breakpoint (\d+),', pexpect.EOF, pexpect.TIMEOUT], 60)
                if index == 0:
                    before = sh.before.replace('\x00', '').strip()
                    after = sh.after.replace('\x00', '').strip()
                    print('####BREAK\n%s\n@@@@\n%s\n####' % (before, after))
                    bidx = int(sh.match.group(1))
                index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 1) ##########
                if index == 0:
                    before = sh.before.replace('\x00', '').strip()
                    after = sh.after.replace('\x00', '').strip()
                    print('####PROMPT\n%s\n@@@@\n%s\n####' % (before, after))
                '''
                while True: 
                    index = sh.expect([prompt, pexpect.EOF, pexpect.TIMEOUT], 30)
                    if index == 0:
                        before = sh.before.replace('\x00', '').strip()
                        after = sh.after.replace('\x00', '').strip()
                        print('####CONTINUE\n%s\n@@@@\n%s\n####' % (before, after))
                        p_b = re.compile(r'.*Breakpoint (\d+),', re.S)
                        bidx = int(p_b.match(before).group(1))
                        break
                    if index == 1:
                        break
                '''
                msg = 'Breakpoint %d' % (bidx)
                vars = self.vars[bidx - 1].split('|')
                bpuobj = bpu.Bpu()
                for var in vars: 
                    name = var.split()[0].strip()
                    handler = var.split()[1].strip()
                    extra = var.split()[2].strip()
                    func = bpuobj.get_handler(handler)
                    if func is None:
                        self.logger.error('invalid handler %s' % (name))
                        break
                    if extra != 'None':
                        msg = '%s, %s\n' % (msg, extra)
                    try:
                        temp = func(sh, name)
                    except Exception, e:
                        self.logger.error(e) 
                        traceback.print_exc(file=sys.stdout)
                        msg = None
                        break
                    if temp is None:
                        msg = None
                        break
                    msg += temp
                    if vars.index(var) < len(vars) - 1:
                        msg += '\n'
                if msg is not None:
                    print('######LOG######\n%s\n######END######' % (msg))
                    self.logger.info('%s' % (msg))
            ret = self.con.send_echo('q', r'\(y or n\)')
            ret = self.con.send_echo('y', r'#')  
            self.logger.debug('exit gdb')
            self.con.close_sh(sh)
            self.recover(rm_paths)
        except AttributeError, e:
            self.logger.error(e) 
            traceback.print_exc(file=sys.stdout)
            return -1
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        except pexpect.exceptions.EOF, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        except pexpect.exceptions.TIMEOUT, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        finally:
            #self.queue.put({'event': 'exit', 'pid': os.getpid()})
            self.queue.put({'event': 'exit', 'pid': self.ident}) 

    def recover(self, rm_paths, mv_paths=None):
        """恢复交换机环境
        Args:
            rm_paths: 复制到交换机和在交换机上新建的文件或目录，调试结束后需删除
            mv_paths: 交换机上备份的文件或目录，调试结束后需恢复
        Returns:
            0: 成功
            -1: 失败
        """
        if rm_paths is None:
            return 0
        try:
            self.con.start_sh()
            for file in rm_paths:
                self.con.single_cmd('rm -rf %s' % (file), [r'#'])
            if mv_paths is not None:
                for file in mv_paths:
                    self.con.single_cmd('mv %s%s %s' % (file, '.bak', file), [r'#'])
            return 0
        except AttributeError, e:
            self.logger.error(e) 
            traceback.print_exc(file=sys.stdout)
            return -1   
        except pexpect_tools.PexpcError, e:
            self.logger.error(e)
            traceback.print_exc(file=sys.stdout)
            return -1
        finally:
            self.logger.debug('recover files complete')
            self.con.close_sh()

    def close_sh_con(self):
        """关闭交换机shell连接
        Args:
            None
        Returns:
            0: 成功
            -1: 失败
        """
        if self.con is not None and self.con.expsh.isalive():
            try:
                self.con.close_sh()
                self.con = None
                self.logger.debug('close sh connetion complete')
            except pexpect_tools.PexpcError, e:
                traceback.print_exc(file=sys.stdout)
                self.logger.error(e)
                return -1
        return 0
    
class MiniLogger(object):
    """简单日志类
    Attributes:
        logger: 日志对象
        logfile: 日志文件路径
        basepath: 日志文件根路径
    """
    def __init__(self, name, file='temp.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logfile = file
        self.basepath = './log/'

    def initialize(self):   
        '''初始化日志配置
        Args:
            None
        Returns:
            self.logger: 配置后的日志对象
        '''
        if not os.path.exists(self.basepath):
            os.mkdir(self.basepath)
        console = logging.handlers.RotatingFileHandler(self.basepath + self.logfile, 'a', 
                                                       10*1024*1024, 10, 'utf-8')
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
                        '[%(levelname)s][%(name)s][%(asctime)s]' +
                        #' %(filename)s, in %(funcName)s() %(threadName)s - %(message)s'
                        '%(message)s'
                        #,'%Y-%m-%d,%H:%M:%S'
                    )
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        return self.logger

if __name__ == '__main__':
    debugger = XorplusDebugger()
    if debugger.parse_arg() != 0:
        exit()
    debugger.start_debug()
    '''
    rm_files = ['/tmp/libsw/libpthread-2.6.1.so', '/tmp/libsw/libpthread.so',
                '/tmp/libsw/libthread_db-1.0.so', '/tmp/libsw/libpthread.so.0', 
                '/tmp/libsw/libthread_db.so.1', '/tmp/libsw/libthread_db.so']
    mv_files = ['/tmp/libsw/libpthread-2.6.1.so', '/tmp/libsw/libpthread.so',
                '/tmp/libsw/libthread_db-1.0.so', '/tmp/libsw/libpthread.so.0', 
                '/tmp/libsw/libthread_db.so.1', '/tmp/libsw/libthread_db.so']
    '''

