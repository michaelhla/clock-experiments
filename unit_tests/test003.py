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



IP = "10.250.55.253"
Port = 8080


msg_q = []
gconn_list = []
connlock = threading.Lock()
machine_ID = 2

# Tests if correct logical clock timestamp is applied when a message is sent 
# assuming one machine is already being run elsewhere


def msg_connect(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    if conn is None:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((IP, port))

    connlock.acquire(timeout=10)
    gconn_list.append(conn)
    connlock.release()

def msg_connect_and_send(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    if conn is None:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((IP, port))

    connlock.acquire(timeout=10)
    gconn_list.append(conn)
    connlock.release()

    connlock.acquire(timeout=10)
    #sends double message
    sender = machine_ID.to_bytes(1, "big")
    clock_val = str(100).encode()
    conn.sendall(sender + clock_val)
    connlock.release()





class Test(unittest.TestCase):
    
    def test(self):
        msg_connect(None, IP, Port)
        time.sleep(5)
        msg_connect_and_send(None, IP, Port)
        time.sleep(5)
        with open("log_1.txt", "r") as f:
            log = f.read()
            self.assertTrue("RecMsg" in log)
            for line in f:
                if "RecMsg" in line:
                    self.assertTrue(str(101) in log)
            f.close()


# Server should be killed after test run

if __name__ == '__main__':
    unittest.main()
