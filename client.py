import socket
import select
import sys


class Client:
	def __init__(self, ip_address, port):
		self.IP_address = ip_address
		self.Port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((self.IP_address, self.Port))
		self.connected = True

	def handle_username(self):
		while True:
			print("Please enter your username")
			username = (sys.stdin.readline()).strip()
			if 20 > len(username) > 2:
				self.server.send(username.encode())
				name_taken = self.server.recv(1024)
				if name_taken == b'1':
					print("Name already taken")
					continue
				else:
					break
			else:
				print('Select a username between 3 and 20 characters')

	def handle_coms(self):
		while self.connected:
			sockets_list = [sys.stdin, self.server]
			read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])
			for socks in read_sockets:
				if socks == self.server:
					message = (socks.recv(2048)).decode('utf-8')
					if message == "":
						self.connected = False
						break
					print(message)
				else:
					message = (sys.stdin.readline()).strip()
					if message == "/exit":
						self.connected = False
						break
					self.server.send(message.encode())
					sys.stdout.write("<You>")
					sys.stdout.write(message + " \n")
					sys.stdout.flush()
		self.server.close()


client = Client("127.0.0.1", 65432)
client.handle_username()
client.handle_coms()
