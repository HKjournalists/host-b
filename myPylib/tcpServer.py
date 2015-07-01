from socket import *
from time import ctime

class TCPServer:
	def __init__(self, host='127.0.0.1', port=10086, buffer=1024):
		self.addr = (host, port)
		self.buffer = buffer
		self.tcpSocket = None
	
	def init_sock(self):
		self.tcpSocket = socket(AF_INET, SOCK_STREAM)
		self.tcpSocket.bind(self.addr)
		self.tcpSocket.listen(20)

	def communicate(self):
		try:
			while True:
				client_sock , client_addr = self.tcpSocket.accept()
				print('conncet from %s' % (client_addr,))
				while True:
					data = client_sock.recv(self.buffer)
					if not data:
						client_sock.close()
						print('connect end')
						break
					client_sock.send('[%s] : %s' % (ctime(), 'hello'))
					#client_sock.close()
		except (EOFError, KeyboardInterrupt):			
			self.tcpSocket.close()

if __name__ == '__main__':
	ts = TCPServer()
	ts.init_sock()
	ts.communicate()
	
