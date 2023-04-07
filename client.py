import socket
import sys
import threading
import os

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

    def recv_messages(self):
        """This method handles receiving messages from the server"""
        while self.connected:
            try:
                message = (self.server.recv(2048)).decode('utf-8')
                if message == "":
                    self.connected = False
                    os._exit(0)
                print(message)
            except Exception as e:
                print(f"Error: {e}")
                self.connected = False
                return

    def send_messages(self):
        """This method handles sending messages to the server and the exit command"""
        while self.connected:
            try:
                message = (sys.stdin.readline()).strip()
                if message == "/exit":
                    self.connected = False
                    os._exit(0)
                self.server.send(message.encode())
            except Exception as e:
                print(f"Error: {e}")
                self.connected = False
                return

    def start(self):
        """Starts the communication and send message threads"""
        self.handle_username()
        recv_thread = threading.Thread(target=self.recv_messages)
        send_thread = threading.Thread(target=self.send_messages)
        recv_thread.start()
        send_thread.start()
        recv_thread.join()
        send_thread.join()
        self.server.close()

# Instantiates the client class, passes the IP address and port of the server as parameters
client = Client("127.0.0.1", 65432)
client.start()
