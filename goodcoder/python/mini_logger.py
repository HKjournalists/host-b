# -*- coding: utf8 -*-
#!/usr/bin/env python

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
简单日志
Authors: wangbin19@baidu.com
Date:    2015/08/19 21:58:35
"""

import logging
import logging.handlers

class MiniLogger(object):
    """简单日志类
    Attributes:
        logger: 日志对象
        logfile: 日志文件路径
    """
    def __init__(self, name, file='hello.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logfile = file
        #self.initialize()

    def initialize(self):   
        '''初始化日志配置
        Args:
            None
        Returns:
            self.logger: 配置后的日志对象
        ''' 
        console = logging.handlers.RotatingFileHandler(self.logfile, 'a', 2000, 10, 'utf-8')
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
                        '[%(levelname)s][%(name)s]%(asctime)s - "%(filename)s" line %(lineno)d, ' +
                        'in %(funcName)s %(processName)s %(threadName)s : %(message)s',
                        '%Y-%m-%d %H:%M:%S'
                    )
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        return self.logger

if __name__ == '__main__':
    logger = MiniLogger(__name__).initialize()
    logger.info('hello world!')