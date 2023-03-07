import socket
import select
import sys
import threading
from _thread import *


def serverthread(IP, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, port))
    server.listen()
    while True:
        conn, addr = server.accept()
        print(addr[0] + " connected")
        # creates and individual thread for each machine that connects
        start_new_thread(msg_listen, (conn, addr))


def msg_listen(conn, addr):
    # this is where a machine will listen when it recognizes a connection
    while True:
        try:
            conn.recv(2048)
        except Exception as e:
            print(e)
            continue


def running_machine(IP, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((IP, port))
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
            else:
                try:
                    server.send()
                    sys.stdout.flush()
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    this_IP = '10.250.189.78'
    client_list = []
    # usage: python3 machine.py listenPORT targetIP targetPORT...
    # connect to all existing machines
    for i in range(3, sys.argv, 2):
        client_list.append(threading.Thread(
            target=clientthread, args=(sys.argv[i], sys.argv[i+1])))
        client_list[i].start()

    # then start its own connection listen thread
    threading.Thread(target=serverthread, args=(this_IP, sys.argv[2]))
