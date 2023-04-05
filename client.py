import socket
import select
import sys

class Client:
	"""This class handles the client side of the chat application"""
	def __init__(self, ip_address, port):
		"""Constructor for the client class
		Arguments:
			ip_address {str} -- The IP address of the server
			port {int} -- The port of the server
		"""
		self.IP_address = ip_address
		self.Port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((self.IP_address, self.Port))
		self.connected = True

	def handle_username(self):
		"""This method handles the selection of a username and checks if it is taken"""
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
		"""This method handles the communication between the client and the server and the exit command"""
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

# Instantiates the client class
client = Client("127.0.0.1", 65432)
client.handle_username()
client.handle_coms()
