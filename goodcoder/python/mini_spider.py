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
import re
import sys
import json
import time
import zlib
import logging
import logging.handlers
import urllib2
import argparse
import threading
import Queue
import HTMLParser 
import ConfigParser

class MiniSpider(object):
    """简单爬虫程序
    Attributes:
        url_list_file: 种子文件路径 
        output_directory: 抓取结果存储目录 
        max_depth: 最大抓取深度(种子为0级) 
        crawl_interval: 抓取间隔. 单位: 秒 
        crawl_timeout: 抓取超时. 单位: 秒 
        target_url: 需要存储的目标网页URL pattern(正则表达式) 
        thread_count: 抓取线程数
        logger: 日志对象
    """
    def __init__(self):
        '''构造方法'''
        self.url_list_file = None          #种子文件路径 
        self.output_directory = None       #抓取结果存储目录 
        self.max_depth = None              #最大抓取深度(种子为0级) 
        self.crawl_interval = None         #抓取间隔. 单位: 秒 
        self.crawl_timeout = None          #抓取超时. 单位: 秒 
        self.target_url = None             #需要存储的目标网页URL pattern(正则表达式) 
        self.thread_count = None           #抓取线程数
        self.url_seeds = None              #初始url种子 
        self.logger = MiniLogger('MiniSpider', 'minisp.log').initialize()
        
    def parse_arg(self):
        '''处理命令行参数
        Args:
            无
        Returns:
            0: 参数正常
            -1: 参数错误
            -2: 配置文件解析失败
        '''
        parser = argparse.ArgumentParser(description='mini spider')
        parser.add_argument('-v', action='version', version='v0.2')
        parser.add_argument('-c', dest='conf', help='path of config file', default = None)
        args = parser.parse_args()
        if args.conf is not None:
            if self.parse_cfg(args.conf) != 0:
                return -2
        else:
            print('no arguments! use [-h] [-v] or [-c CONF]')
            return -1
        return 0

    def parse_cfg(self, file):
        '''处理配置文件
        Args:
            file: 配置文件路径
        Returns:
            0: 正常处理
            -1: 配置文件出错
        '''
        parser = ConfigParser.ConfigParser()
        self.logger.debug('loading config file')
        try:
            parser.read(file)
            kvs = parser.items('spider')
        except ConfigParser.NoSectionError, e:
            self.logger.error(e)
            return -1
        for k, v in kvs:
            if k not in self.__dict__:
                self.logger.error('invalid attribite: %s' % k)
            else:
                self.__dict__[k] = v
        if not os.path.isfile(self.url_list_file):
            self.logger.error('attribite error: url_list_file')
            return -1
        if re.match(r'\d+', self.max_depth) is None:
            self.logger.error('attribite error: max_depth')
            return -1
        if re.match(r'\d+', self.crawl_interval) is None:
            self.logger.error('attribite error: crawl_interval')
            return -1
        if re.match(r'\d+', self.crawl_timeout) is None:
            self.logger.error('attribite error: crawl_timeout') 
            return -1
        if re.match(r'\d+', self.thread_count) is None:
            self.logger.error('attribite error: thread_count')
            return -1 
        if self.target_url is None:
            self.logger.error('attribite error: target_url')
            return -1
        if not os.path.isdir(self.output_directory):
            try: 
                os.makedirs(self.output_directory)
            except OSError, e:
                self.logger.error(e)
                return -1
        self.max_depth = int(self.max_depth)
        self.logger.info('max depth : %d' % (self.max_depth))
        self.crawl_interval = int(self.crawl_interval)
        self.logger.info('interval : %d' % (self.crawl_interval))
        self.crawl_timeout = int(self.crawl_timeout)
        self.logger.info('timeout : %d' % (self.crawl_timeout))
        self.thread_count = int(self.thread_count)
        self.logger.info('thread count : %d' % (self.thread_count))
        self.logger.debug('load config file complete')
        #print(re.match(self.target_url, 'http://awefv.z.w.e.d.gif').group())
        return 0

    def read_seed(self):
        '''读取种子文件
        Args:
            None
        Returns:
            0: 正常执行
            -1: 种子文件出错
        '''
        urls = []
        self.logger.debug('loading seed file')
        with open(self.url_list_file, 'r') as fp:
            urls = [ line.strip() for line in fp ]
            #for line in fp:
            #    urls.append(line.strip())
        if len(urls) == 0:
            self.logger.error('load seed file failed(or the file is empty)')
            return -1
        #print urls
        self.url_seeds = urls
        self.logger.debug('load seed file complete')
        return urls

    def weave(self):
        '''负责分配spider线程
        Args:
            urls: url种子列表
        Returns:
            0: 正常执行
            -1: 种子文件出错
        '''
        self.logger.debug('begin to dispatch threads')
        urls = self.url_seeds
        count_u = len(urls)          #种子数
        count_p = int(self.thread_count)     #最大线程数  
        self.logger.info('seed count: %d, thread count: %d' % (count_u, count_p))   
        lists = [ [] for i in range(count_p)]    #每个线程的初始种子队列
        global_depth = 0        #全局搜索深度
        index = 0
        for url in urls:      
            lists[index % count_p].append(url)   #将传入种子分配至每个线程
            index += 1
        if count_u >= count_p:
            #初始种子数不小于并发线程数，每个线程至少分配到一个种子，可直接开始搜索
            self.logger.debug('dispatch complete')
            self.spawn(count_p, lists)
        else:       #初始种子数小于并发线程数，先按种子数量进行多线程抓取
            while global_depth <= self.max_depth:
                #将max_depth传入spawn中，即只执行一层搜索，目的是取得更多url种子
                self.logger.debug('search for more seeds')
                urls = self.spawn(count_u, lists[:count_u], self.max_depth, 
                                  Queue.Queue(maxsize=pcount))
                global_depth += 1
                if len(urls) >= count_p:   #已获取足够的种子数，跳出
                    break
            #种子数满足线程数需求，且没有达到最大搜索深度，重新分配种子并在全局深度继续搜索       
            if global_depth <= self.max_depth:   
                index = 0
                for url in urls:      
                    lists[index % count_p].append(url)
                    index += 1
                self.logger.debug('dispatch complete')
                self.spawn(count_p, lists, global_depth)
        return 0

    def spawn(self, pcount, lists, local_depth=0, queue=None):
        '''爬虫线程生成器
        Args:
            pcount: 生成线程个数
            lists: 线程初始种子列表，表中的元素是分配给每个线程的种子列表，例如：
                   [[p1url1, p1url2, ...] ,[p2url1, p2url2, ...], ...]
            local_depth: 当前搜索深度
            queue: 用于储存线程返回数据的队列，当需要返回数据时传入Queue.Queue对象
                   否则不需传入参数
        Returns:
            urls: 所有爬虫线程返回的url汇总
            0: 正常执行（无返回数据）
        '''
        threads = []
        for i in range(pcount):
            t = threading.Thread(target=self.bfspider, args=(lists[i], local_depth, queue))
            threads.append(t)
        for i in threads:
            i.start()
        #while not queue.full():
        #    pass
        #while not queue.empty():
        if queue:
            urls = []
            limit = pcount
            while limit > 0:
                list = queue.get()
                if len(list) != 0:
                    urls.extend(list)
                limit -= 1
            return urls
        for i in threads:
            i.join()
        return 0

    def bfspider(self, urls, depth, queue):
        '''带深度数限制的广度优先搜索
        Args:
            urls: url种子列表
            depth: 起始深度
            queue: 用于储存线程返回数据的队列，参数为None时不返回数据
        Returns:
            0: 正常执行
        '''
        self.logger.debug('new spider thread')
        count = len(urls)
        interval = self.crawl_interval
        parser = StaticParser(self.target_url)
        parser.init_set(urls)
        while depth <= self.max_depth and len(urls) != 0:
            if interval is not None and interval > 0:
                time.sleep(interval)
            url = urls.pop(0)
            ret = parser.explore(url)
            if type(ret) == list:
                urls.extend(ret)
            elif type(ret) == int:  #请求url失败
                pass
            count -= 1
            if count == 0:
                depth += 1
                count = len(urls)
        if queue:
            queue.put(urls)
        self.logger.debug('spider thread finish')
        return 0

class StaticParser(HTMLParser.HTMLParser):
    '''静态html解析器
    Attributes:
        stack: 用于建立dom节点树结构的堆栈
        document: dom元素根节点
        cur_node: 当前解析的节点
        charset: 当前页面编码
        basepath: 当前页面的基地址
        target_url: 需要保存的url
        logger: 日志对象
    '''
    urlset = set([])   #记录已访问url的类变量
    mutex = threading.Lock()     #互斥锁，用于对urlset操作时的线程同步
    def __init__(self, target_url):
        HTMLParser.HTMLParser.__init__(self)
        self.stack = []
        self.document = None
        self.cur_node = None
        self.charset = None
        self.basepath = None
        self.target_url = target_url
        self.logger = MiniLogger('StaticParser', 'minisp.log').initialize()

    def init_set(self, urls):
        '''初始化urlset
        Args:
            urls: 初始化url列表
        Returns:
            0: 正常执行
        '''
        if self.__class__.mutex.acquire():
            if len(self.__class__.urlset) == 0:
                [self.__class__.urlset.add(i) for i in urls]
            self.__class__.mutex.release()
        return 0

    def visited(self, url):
        '''判断url是否已经访问
        Args:
            url: url地址
        Returns:
            True: url已经被访问
            False: url未被访问
        '''
        flag = False
        if self.__class__.mutex.acquire():  
            if url in self.__class__.urlset:
                flag = True
            else:
                self.__class__.urlset.add(url)
            self.__class__.mutex.release()
            #if not flag:
                #print('%s hasn't been visited' % (url))
            #print('%s has been visited' % (url))
            return flag    

    def download_url(self, url):
        '''下载url
        Args:
            url: url地址
        Returns:
            data: 下载到的数据
            -1: 无法请求url
        '''
        self.logger.debug('downloading %s' % (url))
        req_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)\
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
            self.logger.error('request url %s failed' % (url))
            return -1
        except urllib2.URLError, e:
            self.logger.error('name or service not known : %s' % (url))
            return -1
        except ValueError, e:
            self.logger.error('illegal url : %s' % (url))
            return -1
        data = res.read()
        info = res.info()
        if(("Content-Encoding" in info) and (info['Content-Encoding'] == "gzip")) :
            data = zlib.decompress(data, 16+zlib.MAX_WBITS);
        #print res.__dict__
        self.logger.debug('downloading %s complete' % (url))
        return data

    def save_url(self, url):
        '''保存url
        Args:
            url: url地址
        Returns:
            data: 下载到的数据
            -1: 无法请求url
        '''
        data = self.download_url(url)
        file = './downloads/' + url.replace('/', '#')
        with open(file, 'w+') as fp:
            fp.write(data)
        self.logger.info('download url %s' % (url))
        return 0

    def handle_starttag(self, tag, attrs):
        '''处理开始标记
        Args:
            tag: 读取到的html标记名
            attrs: html标记的属性
        Returns:
        '''
        if tag == 'meta' and attrs:
            content_re = re.compile(r'charset\s*=\s*([a-zA-Z0-9-]*)\s*')
            charset_re = re.compile(r'\s*([a-zA-Z0-9-]*)\s*')
            for (k, v) in attrs:
                if k == 'content' and content_re.match(v):
                    self.charset = content_re.match(v).group(1)
                elif k == 'charset' and charset_re.match(v):
                    self.charset = charset_re.match(v).group(1)
        node = DomNode(self.cur_node, tag, attrs)
        self.cur_node.add_child(node)
        self.stack.append(node)
        self.cur_node = node
    
    def handle_startendtag(self, tag, attrs):   
        '''处理开始-结束标记
        Args:
            tag: 读取到的html标记名
            attrs: html标记的属性
        Returns:
        '''
        #if tag == 'img':
        #    if len(attrs) != 0: 
        #        for (name, value) in attrs:
        #            if name == 'src':
        #                print value.strip()             

    def handle_data(self, data):
        '''处理标记间的数据
        Args:
            data: 读取到的html标记中的数据
        Returns:
        '''
        if self.charset:
            data = data.decode(self.charset)
        if data.strip():
            #data = data.decode(self.charset)
            #print('set data of node %s: %s' % (self.cur_node.tag, data))
            self.cur_node.data = data

    def handle_endtag(self, tag):
        '''处理结束标记
        Args:
            tag: 读取到的html标记名
        Returns:
        '''
        #print('node end: %s' % (tag))
        if self.stack:
            node = self.stack.pop()
            #print('pop node: %s' % (node.tag))
            while self.stack and node.tag != tag:
                node.modify()
                node = self.stack.pop()
            self.cur_node = node.parent

    def explore(self, url):
        '''搜索页面内容
        Args:
            url: 待搜索的url
        Returns:
            -1: 请求url失败
        '''
        self.logger.info('visit %s' % (url))
        html = self.download_url(url)
        if type(html) == int:
            return -1
        scheme = ''
        specific = url.split(r'://')
        if len(specific) == 2:
            scheme = specific[0].strip() + '://'
            specific = specific[1].strip()
        else:
            specific = specific[0].strip()
        index = specific.rfind('/')
        if index == len(specific) -1:  #url以'/'结尾
            self.basepath = url
        elif index == -1:       #url不以'/'结尾，加上'/'
            self.basepath = url + '/'
        else:    #url不以'/'结尾但包含'/'，如www.a.com/b/c.html，获取当前根路径
            self.basepath = scheme + specific[:index + 1] 
        self.document = DomNode(tag='document')
        self.cur_node = self.document
        self.logger.debug('build dom tree')
        self.feed(html)   #读取url建立dom树
        list = []
        #self.document.bfs()
        self.logger.debug('parse dom tree')
        self.document.dfs(0, self.parse_node, list)
        #print list
        #print self.__class__.urlset
        return list

    def parse_node(self, node, list):
        '''处理dom节点，判断是否需要下载或添加进遍历列表中
        Args:
            node: 当前dom节点
            list: 储存用于返回的url列表
        Returns:
            0: 正常处理dom节点且未发现需要后续访问的url
            -1: 节点属性为空
            -2: 节点中没有符合要求的url
            url: 正常处理节点且发现需要后续访问的url
        '''
        if node.attrs is None:
            self.logger.debug('node %s has no attributes, skip' % (node.tag))
            return -1
        js_url_p = re.compile(r'^\s*javascript:\s*(.*)$', re.I)   #匹配js跳转
        js_re = r'^(((top)|(self)|(parent)|(this))\.)?location\.href[ \t]*=[ \t]*.*$'
        js_loc_p = re.compile(js_re, re.I)
        abs_url_p = re.compile(r'^([a-zA-Z.+\-]+:)?//.*$')  #匹配绝对地址
        http_p = re.compile(r'^https?://.*', re.I)          #匹配http(s)协议的url
        slash_p = re.compile(r'^/+(.*)')                    #匹配相对地址开头的斜线
        #rel_url_p = re.compile(r'^\w+.*$')                 #匹配相对地址（暂不使用）
        target_p = re.compile(self.target_url, re.I)        #需要保存的url
        url = None
        if node.tag == 'base':                     #检测base标签    
            for (tag, val) in node.attrs:
                if tag == 'href':
                    self.basepath = val
                    self.logger.debug('found base url %s' % (val))
                    return 0
        elif node.tag == 'a':
            #list.append(node.attrs)
            for (tag, val) in node.attrs:
                if tag == 'href':
                    #print tag, val
                    url = val
                    match = js_url_p.match(val)
                    if match:                      #js跳转，取出js中的地址
                        val = match.group(1)
                        if val and js_loc_p.match(val):
                            url = val.split('=')[1].strip().replace('"', '').replace('\'', '')     
                            break
        elif node.tag == 'img':
            #list.append(node.attrs)
            for (tag, val) in node.attrs:
                if tag == 'src':
                    #print tag, val
                    url = val
                    break
        if url is None:
            self.logger.debug('no available url in node %s' % (node.tag))
            return -2
        match = abs_url_p.match(url)
        if not match:                   #url不匹配绝对地址，则认为是相对地址
            match = slash_p.match(url)
            if match:
                url = match.group(1)    #去掉相对地址开头的斜线
            url = self.basepath + url   #转化为绝对地址
        if not self.visited(url):       #判断是否已经加入访问队列
            if target_p.match(url):    
                self.save_url(url)      #保存url
            if http_p.match(url):
                print('append %s' % (url))
                list.append(url)
                #return url
        return 0 

class DomNode(object):
    '''简单dom节点
    Attributes:
        parent: 当前节点的父元素
        tag: 当前节点标记名
        attrs: 节点属性
        data: 节点数据（标记间的内容）
        children: 节点的子节点列表
    '''
    def __init__(self, parent=None, tag=None, attrs=None, data=None):
        self.parent = parent
        self.tag = tag
        self.attrs = attrs
        self.data = data
        self.children = []

    def add_child(self, node):
        '''添加子节点
        Args:
            node: 待添加的节点
        Returns:
            0: 成功
        '''
        #print('add node: %s' % (node.tag))
        node.parent = self
        self.children.append(node)
        return 0

    def modify(self):
        '''修正dom树，将当前节点的子节点变为自己的兄弟节点
        Args:
            None
        Returns:
            0: 成功
        '''
        #print('rm node: %s' % (self.tag))
        for n in self.children:
            n.parent = self.parent
        self.parent.children.extend(self.children)
        self.children = []
        #self.parent.children.remove(self)
        #del self
        return 0

    def bfs(self, hook=None, list=None):
        '''对dom节点进行广度优先遍历
        Args:
            list: 储存用于返回的url列表
        Returns:
            0: 成功
        '''
        list = [self]
        count = len(list)
        depth = 0
        while len(list) != 0:
            node = list.pop(0)
            parent = node.parent.tag if node.parent else ''
            hook(self, list) if hook else self.default_hook(depth)
            #if hook is None:
            #    self.default_hook(depth)
            #else:
            #    ret = hook(self)
            #    if type(ret) == str:
            #        list.append(ret)
            list.extend(node.children)
            count -= 1
            if count == 0:
                depth += 1
                count = len(list)
        return 0

    def dfs(self, depth, hook=None, list=None):
        '''对dom节点进行深度优先遍历
        Args:
            depth: 用于调整打印输出时的缩进（不打印时此参数无意义）
            hook: 遍历节点时调用的钩子函数，包含两个参数，当前dom节点和用于返回url的列表
            list: 储存用于返回的url列表
        Returns:
            0: 成功
        '''
        parent = self.parent.tag if self.parent else ''
        hook(self, list) if hook else self.default_hook(depth)
        #if hook is None:
        #    self.default_hook(depth)
        #else:
        #    ret = hook(self)
        #    if type(ret) == str:
        #        list.append(ret)
        if self.children:
            for node in self.children:
                node.dfs(depth + 1, hook, list)
        return 0

    def default_hook(self, depth):
        '''默认钩子函数，打印节点信息
        Args:
            depth: 当前深度
        Returns:
            0: 正常
        '''
        if depth > 0:
            depth -= 1
        element = '%s<%s' % (' ' * 4 * depth, self.tag)
        if self.attrs:
            for (k, v) in self.attrs:
                element += ' %s=\'%s\'' % (k, v)
        element += '>'
        if self.data:
            element += self.data
        print(element)
        return 0

class MiniLogger(object):
    """简单日志类
    Attributes:
        logger: 日志对象
        logfile: 日志文件路径
    """
    def __init__(self, name, file='hello.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logfile = file

    def initialize(self):   
        '''初始化日志配置
        Args:
            None
        Returns:
            self.logger: 配置后的日志对象
        ''' 
        console = logging.handlers.RotatingFileHandler(self.logfile, 'a', 10*1024*1024, 10, 'utf-8')
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
                        '[%(levelname)s][%(name)s]%(asctime)s - "%(filename)s" line %(lineno)d, ' +
                        'in %(funcName)s %(processName)s %(threadName)s - %(message)s',
                        '%Y-%m-%d %H:%M:%S'
                    )
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        return self.logger

if __name__ == '__main__':
    ms = MiniSpider()
    if ms.parse_arg() != 0:
        exit()
    ms.read_seed()
    ms.weave()
    #ms.bfspider(['http://pycm.baidu.com:8081'], 0, None)
    #if ret != -1:
    #    ms.weave(ret)
    #sp = StaticParser(r'.*\.(gif|png|jpg|bmp)$')
    #sp.download_url('a')
    #sp.explore('http://www.baidu.com')
    #sp.explore('http://pycm.baidu.com:8081')