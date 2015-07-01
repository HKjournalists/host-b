from socket import *

class tcpClient:
	def __init__(self, host='127.0.0.1',port=10086,buffer=1024):
		self.addr = (host, port)
		self.buffer=1024
		
	
	def init(self):
		tcpClient = socket(AF_INET, SOCK_STREAM)
		tcpClient.connect(self.addr)

		while True:
			data = raw_input('>')
			if not data:
				break
			tcpClient.send(data)
			data = tcpClient.recv(self.buffer)
			if not data:
				break
			print data
		tcpClient.close()
		
if __name__ == '__main__':
	tc = tcpClient()
	tc.init()
