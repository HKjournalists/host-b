#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib2

res = urllib2.urlopen('http://www.baidu.com/') 
html = response.read()  
print html
