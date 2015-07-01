#!/usr/bin/env python

import socket

class udpClient:
	def __init__(self, host='127.0.0.1', port=10086, buffer=1024):
		self.addr = (host, port)
		self.buffer = buffer

	def init(self):
		udp_c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			while True:
				data = raw_input('>')
				if not data:
					break
				udp_c.sendto(data, self.addr)
				data , addr = udp_c.recvfrom(self.buffer)
				if not data:
					break
				print data
			udp_c.close()
		except (Exception, KeyboardInterrupt):
			udp_c.close()

if __name__ == '__main__':
	uc = udpClient()
	uc.init()
