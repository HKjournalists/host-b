# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
简单爬虫程序
Authors: wangbin19@baidu.com
Date:    2015/07/23 19:32:35
"""

import os
import sys
import json
import re
import zlib
import urllib2
import argparse
import ConfigParser
import Queue
import threading
import time
import random

import mini_logger

class MiniSpider:
    urlset = set([])   #记录已访问url的类变量
    mutex = threading.Lock()
    count = 0
    def __init__(self):
        '''构造方法
        Args:
            无
        Returns:
            无
        '''
        self.url_list_file = None          #种子文件路径 
        self.output_directory = None       #抓取结果存储目录 
        self.max_depth = None              #最大抓取深度(种子为0级) 
        self.crawl_interval = None         #抓取间隔. 单位: 秒 
        self.crawl_timeout = None          #抓取超时. 单位: 秒 
        self.target_url = None             #需要存储的目标网页URL pattern(正则表达式) 
        self.thread_count = None           #抓取线程数          
        self.b = B()   
        self.__class__.count += 1
        

    def parse_arg(self):
        '''处理命令行参数
        Args:
            无
        Returns:
            0: 参数正常
            -1: 配置文件解析失败
        '''
        parser = argparse.ArgumentParser(description='mini spider')
        parser.add_argument('-v', action='version', version='v0.1')
        parser.add_argument('-c', dest='conf', help='path of config file', default = None)
        args = parser.parse_args()
        if args.conf is not None:
            if not os.path.isfile(args.conf):
                print('config file not exists: %s' % (args.conf))
            if self.parse_cfg(args.conf) != 0:
                return -1
        else:
            print('no arguments! use [-h] [-v] or [-c CONF]')

    def parse_cfg(self, file):
        '''处理配置文件
        Args:
            file: 配置文件路径
        Returns:
            0: 正常处理
            -1: 配置文件出错
            -2: 配置文件内容出错
        '''
        parser = ConfigParser.ConfigParser()
        try:
            parser.read(file)
            kvs = parser.items('spider')
        except ConfigParser.NoSectionError, e:
            #print(e)
            return -1
        for k, v in kvs:
            if k not in self.__dict__:
                self.__dict__[k] = v
        for k in self.__dict__:
            if self.__dict__[k] == None:
                #print('config file error!')
                return -2
        return 0

    def process(self, queue):
        print('process start')
        time.sleep(3)
        number = random.randint(1,10)
        visited = False
        if self.__class__.mutex.acquire():  
            if number in self.__class__.urlset:
                visited = True
            else:
                self.__class__.urlset.add(number)
            self.__class__.mutex.release()
            if not visited:
                print('not visited, put %d in queue' % (number))
                #queue.put(number)
            else:
                print('%d has been visited' % (number))
        print('process complete')

    def manager(self):
        myqueue = Queue.Queue(maxsize = 5)
        arr = []
        for i in range(20):
            t = threading.Thread(target=self.process, args=(myqueue,))
            arr.append(t)
        for i in arr:
            i.start()
        #while not myqueue.full():
        #    pass
        #while not myqueue.empty():
        #    print myqueue.get()
        for i in arr:
            i.join()
        print('finish')
        print self.__class__.urlset   
        print self.__class__.count    
    
    def download_url(self, url):
        '''下载html页面
        Args:
            url: url地址
        Returns:
            data: 下载到的页面内容
            -1: 无法请求url
        '''
        req_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (Kdata, like Gecko)\
             Chrome/44.0.2403.89 Safari/537.36',
            'Accept': 'text/html;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8,GB2312;q=0.7,*;q=0.3',
            'Accept-Encoding': 'gzip',
            'Connection': 'close',
            'Referer': None  
        }
        req_timeout = 10
        req = urllib2.Request(url, None, req_header)
        req.add_header('Accept-Encoding', 'gzip');
        try:
            res = urllib2.urlopen(req, None, req_timeout)
        except urllib2.HTTPError, e:
            #print e.code
            return -1
        except ValueError, e:
            #print e
            return -1
        data = res.read()
        info = res.info()
        if(("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")) :
            data = zlib.decompress(data, 16+zlib.MAX_WBITS);
        #print res.__dict__
        #print data
        #print info
        #print res.url
        return data

    def functest(self):
        logger = mini_logger.MiniLogger('test').initialize()
        #logger.log('info', 'hello world!')
        logger.info('hello world!')
        return 0

class B:
    def __init__(self):
        self.count = 1

    def change(self, list):
        list.extend([5,6,7,8])


if __name__ == '__main__':
    ms = MiniSpider()
    #list = [1,2,3,4]
    #print ms.functest()
    ms.functest()

    