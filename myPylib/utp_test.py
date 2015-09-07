#!/usr/bin/env python

import socket
from time import ctime

class udpServer:
	def __init__(self, host='127.0.0.1', port=10086, buffer=1024):
		self.addr = (host, port)
		self.buffer = buffer

	def init(self):
		udp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udp_s.bind(self.addr)

		try:	
			while True:
				data , addr = udp_s.recvfrom(self.buffer)
				print('udp datagram from %s' % (addr, ))
				print('data: %s' % (data, ))
				udp_s.sendto('[%s] : %s' % (ctime(), data), addr)


		except (Exception, KeyboardInterrupt):
			udp_s.close()
		
if __name__ == '__main__':
	us = udpServer()
	us.init()
