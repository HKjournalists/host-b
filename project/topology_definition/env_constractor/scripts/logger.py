# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'wangbin19'

import os
import sys
import datetime

class Logger(object):
	def __init__(self, filepath):
		self.basepath = os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep
		self.filepath = filepath

	def append(self, str):
		file = open(self.filepath, 'a')
		time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		file.write("[" + time + "] " + str)
		file.close()

	def reset(self):
		file = open(self.filepath, 'w')
		file.close()

