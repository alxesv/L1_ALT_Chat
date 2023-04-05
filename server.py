import socket
import sys
import threading
from datetime import datetime

class Server:
    """This class handles the server side of the chat application"""
    def __init__(self, ip_address, port):
        """Constructor for the server class
        Arguments:
            ip_address {str} -- The IP address of the server
            port {int} -- The port of the server
        """
        self.IP_address = ip_address
        self.Port = port
        self.list_of_clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.IP_address, self.Port))
        self.server.listen()
        self.online = True

    @staticmethod
    def log(message):
        """Logs messages to a file
        Arguments:
            message {str} -- The message to be logged
        """
        logfile = "log.txt"
        now = datetime.now()
        with open(logfile, 'a+') as f:
            f.write(now.strftime('%d/%m/%Y %H:%M:%S') + ' - ' + message + '\n')

    def client_thread(self, con, username):
        """This method handles the communication between the server and the client
        Arguments:
            con {socket} -- The connection to the client
            username {str} -- The username of the client
        """
        try:
            con.send(f"Welcome to this chatroom, {username}!".encode())
            while self.online:
                try:
                    message = ((con.recv(2048)).decode('utf_8')).rstrip()
                    if message:
                        message_to_send = f"<{username}> {message}"
                        print(message_to_send)
                        self.broadcast(message_to_send, con)
                    else:
                        self.remove(con)
                except OSError:
                    continue
        except BrokenPipeError:
            return

    def handle_connect(self, connect, addr):
        """This method handles the username of the client and checks if it is taken
        Arguments:
            connect {socket} -- The connection to the client
            addr {str} -- The IP address of the client
        """
        while self.online:
            new_username = (connect.recv(2048).decode('utf-8')).rstrip()
            name_taken = False
            for i in range(len(self.list_of_clients)):
                for client in self.list_of_clients[i]:
                    if self.list_of_clients[i][client] != new_username:
                        continue
                    else:
                        name_taken = True
            if name_taken:
                connect.send(b'1')
            else:
                connect.send(b'0')
                self.list_of_clients.append({connect: new_username})
                print(f"{new_username} connected from {addr[0]}")
                self.log(f"user <{new_username}> logged in from {addr[0]}")
                client_thread = threading.Thread(target=self.client_thread, args=(connect, new_username))
                client_thread.start()
                self.broadcast(f"{new_username} joined the chat!", connect)
                return

    def broadcast(self, message, connection):
        """This method broadcasts the message to all the clients except the sender
        Arguments:
            message {str} -- The message to be broadcasted
            connection {socket} -- The connection to the client that sent the message
        """
        for i in range(len(self.list_of_clients)):
            for clients in self.list_of_clients[i]:
                if clients != connection:
                    try:
                        clients.send(message.encode())
                    except error as e:
                        print(e)
                        clients.close()
                        self.remove(clients)
                        return

    def remove(self, connection):
        """This method removes a client from the list of clients and removes the connection
        Arguments:
            connection {socket} -- The connection to the client to be removed
        """
        for i in range(0, len(self.list_of_clients)):
            for clients in self.list_of_clients[i]:
                if clients == connection:
                    print(f"{self.list_of_clients[i][clients]} disconnected")
                    self.log(f"user <{self.list_of_clients[i][clients]}> logged out")
                    self.broadcast(f"{self.list_of_clients[i][clients]} left the chat!", connection)
                    self.list_of_clients.remove(self.list_of_clients[i])
                    clients.close()
                    return

    def close_server(self):
        """This method closes the server when the user types "close" in the console"""
        while True:
            if sys.stdin.readline().strip() == "close":
                for i in range(len(self.list_of_clients)):
                    for client in self.list_of_clients[i]:
                        client.close()
                self.online = False
                self.server.close()
                return

    def start_server(self):
        """This method starts the server and accepts new connections"""
        close_thread = threading.Thread(target=self.close_server)
        close_thread.start()
        while self.online:
            try:
                conn, addr = self.server.accept()
                connect_thread = threading.Thread(target=self.handle_connect, args=(conn, addr))
                connect_thread.start()
            except ConnectionAbortedError:
                break

# Instantiate the server class, pass the ip address and port as parameters
chat = Server("127.0.0.1", 65432)
chat.start_server()
