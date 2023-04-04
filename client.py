import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = "127.0.0.1"
Port = 65432
server.connect((IP_address, Port))
connected = True

while True:
	print("Please enter your username")
	username = (sys.stdin.readline()).strip()
	if 20 > len(username) > 2:
		server.send(username.encode())
		name_taken = server.recv(1024)
		if name_taken == b'1':
			print("Name already taken")
			continue
		else:
			break
	else:
		print('Select a username between 3 and 20 characters')

while connected:
	sockets_list = [sys.stdin, server]
	read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])
	for socks in read_sockets:
		if socks == server:
			message = (socks.recv(2048)).decode('utf-8')
			if message == "":
				connected = False
				break
			print(message)
		else:
			message = (sys.stdin.readline()).strip()
			if message.strip() == "/exit":
				connected = False
				break
			server.send(message.encode())
			sys.stdout.write("<You>")
			sys.stdout.write(message)
			sys.stdout.flush()

server.close()
