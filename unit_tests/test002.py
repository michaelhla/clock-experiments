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

# Tests if log books start running before full initialization
# assuming we run initial machine elsewhere


def msg_connect(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    if conn is None:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((IP, port))

    connlock.acquire(timeout=10)
    gconn_list.append(conn)
    connlock.release()



class Test(unittest.TestCase):
    
    def test(self):
        msg_connect(None, IP, Port)

        with open("log_1.txt", "r") as f:
            log = f.read()
            self.assertFalse("IntEvent" in log or "RecMsg" in log or "SentMsg" in log or "SentDoubMsg" in log)
            f.close()


# Server should be killed after test run

if __name__ == '__main__':
    unittest.main()
