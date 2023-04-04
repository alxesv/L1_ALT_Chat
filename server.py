import socket
import sys
from _thread import *
from datetime import datetime

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_address = "127.0.0.1"
Port = 65432
server.bind((IP_address, Port))
server.listen()
list_of_clients = []

def log(message):
    logfile = "log.txt"
    now = datetime.now()
    with open(logfile, 'a+') as f:
        f.write(now.strftime('%d/%m/%Y %H:%M:%S') + ' - ' + message + '\n')

def clientthread(con, username):
    try:
        con.send(f"Welcome to this chatroom, {username}!".encode())
        while True:
            try:
                message = ((con.recv(2048)).decode('utf_8')).rstrip()
                if message:
                    message_to_send = f"<{username}> {message}"
                    print(message_to_send)
                    broadcast(message_to_send, con)
                else:
                    remove(con)
            except OSError as e:
                continue
    except BrokenPipeError:
        return

def handleConnect(connect, addr):
    while True:
        new_username = (connect.recv(2048).decode('utf-8')).rstrip()
        name_taken = False
        for i in range(len(list_of_clients)):
            for client in list_of_clients[i]:
                if list_of_clients[i][client] != new_username:
                    continue
                else:
                    name_taken = True
        if name_taken:
            connect.send(b'1')
        else:
            connect.send(b'0')
            list_of_clients.append({connect: new_username})
            print(f"{new_username} connected from {addr[0]}")
            log(f"user <{new_username}> logged in from {addr[0]}")
            start_new_thread(clientthread, (connect, new_username))
            broadcast(f"{new_username} joined the chat!", connect)
            return

def broadcast(message, connection):
    for i in range(len(list_of_clients)):
        for clients in list_of_clients[i]:
            if clients != connection:
                try:
                    clients.send(message.encode())
                except error as e:
                    print(e)
                    clients.close()
                    remove(clients)
                    return

def remove(connection):
    for i in range(0, len(list_of_clients)):
        for clients in list_of_clients[i]:
            if clients == connection:
                print(f"{list_of_clients[i][clients]} disconnected")
                log(f"user <{list_of_clients[i][clients]}> logged out")
                broadcast(f"{list_of_clients[i][clients]} left the chat!", connection)
                list_of_clients.remove(list_of_clients[i])
                clients.close()
                return

def closeServer():
    while True:
        if sys.stdin.readline().strip() == "close":
            server.close()
            return

while True:
    start_new_thread(closeServer, ())
    try:
        conn, addr = server.accept()
        start_new_thread(handleConnect, (conn, addr))
    except ConnectionAbortedError:
        break
