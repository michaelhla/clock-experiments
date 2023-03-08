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
Port1 = 8080
Port2 = 8081


msg_q = []
gconn_list = []
connlock = threading.Lock()
machine_ID = 3

# assume now that two external servers are running. We want to check if send to both functionality works, with correct timestamping


def msg_connect(conn, IP=None, ports=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    name = "log_"+str(machine_ID)+".txt"
    with open(name, "w") as f:
        f.write("LOG_"+str(machine_ID)+"\n")
        f.write("Rate: " + str(1)+"\n")
    if conn is None:
        for port in ports:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(port)
            conn.connect((IP, port))
            sender = machine_ID.to_bytes(1, "big")
            clock_val = str(100).encode()
            conn.sendall(sender + clock_val)

    with open("log_3.txt", "a") as f:
        f.write("SentDoubMsg,"+str(datetime.datetime.now())+","+str(101)+"\n")


class Test(unittest.TestCase):

    def test(self):
        msg_connect(None, IP, [Port1, Port2])
        time.sleep(5)
        with open("log_1.txt", "r") as f:
            log = f.read()
            self.assertTrue("RecMsg" in log)
            for line in f:
                if "RecMsg" in line:
                    self.assertTrue(str(101) in log)
            f.close()

        with open("log_2.txt", "r") as f:
            log = f.read()
            self.assertTrue("RecMsg" in log)
            for line in f:
                if "RecMsg" in line:
                    self.assertTrue(str(101) in log)
            f.close()

        with open("log_3.txt", "r") as f:
            log = f.read()
            self.assertTrue("SentDoubMsg" in log)
            for line in f:
                if "RecMsg" in line:
                    self.assertTrue(str(101) in log)
            f.close()


# Server should be killed after test run
if __name__ == '__main__':
    unittest.main()
