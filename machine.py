import socket
import select
import sys
import threading
from _thread import *


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))


# VERY EARLY BOILERPLATE
# NEED EACH MACHINE TO ACT AS BOTH CLIENT AND SERVER
# From there we just open three terminals and let it run


def listen():
    while True:

        # maintains a list of possible input streams
        sockets_list = [sys.stdin, server]

        """ There are two possible input situations. Either the
        user wants to give manual input to send to other people,
        or the server is sending a message to be printed on the
        screen. Select returns from sockets_list, the stream that
        is reader for input. So for example, if the server wants
        to send a message, then the if condition will hold true
        below.If the user wants to send a message, the else
        condition will evaluate as true"""
        read_sockets, write_socket, error_socket = select.select(
            sockets_list, [], [])

        for socks in read_sockets:
            if socks == server:
                message = socks.recv(2048)
                dmessage = message[1:].decode()
            else:
                message = 'confirm'.encode()
                try:
                    server.send(message)
                    sys.stdout.flush()
                except Exception as e:
                    print(e)


def send():
    """The first argument AF_INET is the address domain of the
    socket. This is used when we have an Internet Domain with
    any two hosts The second argument is the type of socket.
    SOCK_STREAM means that data or characters are read in
    a continuous flow."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if len(sys.argv) != 3:
        print("Correct usage: script, IP address, port number")
        exit()

    # IP address is first argument
    IP_address = str(sys.argv[1])

    # Port number is second argument
    port = int(sys.argv[2])

    # Server initialized at input IP address and port
    server.bind((IP_address, port))

    server.listen()

    while True:
        """Accepts a connection request and stores two parameters,
        conn which is a socket object for that user, and addr
        which contains the IP address of the client that just
        connected"""
        conn, addr = server.accept()

        """Maintains a list of clients for ease of broadcasting
        a message to all available people in the chatroom"""
        # list_of_clients.append(conn)

        # prints the address of the user that just connected
        print(addr[0] + " connected")

        # creates and individual thread for every user
        # that connects
        start_new_thread(listen, (conn, addr))

        conn.close()
        server.close()


threading.Thread(target=listen)
threading.Thread(target=send)
