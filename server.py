import socket
import sys
from _thread import *
from datetime import datetime


class Server:
    def __init__(self, ip_address, port):
        self.IP_address = ip_address
        self.Port = port
        self.list_of_clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.IP_address, self.Port))
        self.server.listen()

    @staticmethod
    def log(message):
        logfile = "log.txt"
        now = datetime.now()
        with open(logfile, 'a+') as f:
            f.write(now.strftime('%d/%m/%Y %H:%M:%S') + ' - ' + message + '\n')

    def client_thread(self, con, username):
        try:
            con.send(f"Welcome to this chatroom, {username}!".encode())
            while True:
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
        while True:
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
                start_new_thread(self.client_thread, (connect, new_username))
                self.broadcast(f"{new_username} joined the chat!", connect)
                return

    def broadcast(self, message, connection):
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
        while True:
            if sys.stdin.readline().strip() == "close":
                self.server.close()
                return

    def start_server(self):
        start_new_thread(self.close_server, ())
        while True:
            try:
                conn, addr = self.server.accept()
                start_new_thread(self.handle_connect, (conn, addr))
            except ConnectionAbortedError:
                break


chat = Server("127.0.0.1", 65432)
chat.start_server()
