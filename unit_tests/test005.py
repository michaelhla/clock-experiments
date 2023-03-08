import socket
import select
import sys
import threading
from _thread import *
import random
import time
import datetime
import unittest
import subprocess
from unittest.mock import patch


hostname = socket.gethostname()
IP = str(socket.gethostbyname(hostname))
Port = 8080


msg_q = []
gconn_list = []
connlock = threading.Lock()
machine_ID = 2
msg_q = []
qlock = threading.Lock()

# Tests machine listening
# assuming we run another machine elsewhere afterwards


def serverthread(IP, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, port))
    server.listen()
    while True:
        conn, addr = server.accept()
        print(addr[0] + " connected")
        # creates an individual thread for each machine that connects
        start_new_thread(msg_listen, (conn,))
        print('TEST005 PASSED')
        return


def msg_listen(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    if conn is None:
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((IP, port))
        except:
            print(f"{IP} connection failed")
            return

    connlock.acquire(timeout=10)
    gconn_list.append(conn)
    connlock.release()

    while True:
        try:
            msg = conn.recv(2048)
            if msg:
                qlock.acquire(timeout=10)
                msg_q.append(msg)
                qlock.release()
                print('TEST005 PASSED')
                return
            if not msg:
                print(str(conn) + " disconnected")
                connlock.acquire(timeout=10)
                gconn_list.remove(conn)
                connlock.release()
                return

        except Exception as e:
            print(e)
            print('TEST005 FAILED')
            return


# Server should be killed after test run
if __name__ == '__main__':
    serverthread(IP, Port)
