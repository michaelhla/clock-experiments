import socket
import select
import sys
import threading
from _thread import *
import random
import time

msg_q = []
qlock = threading.Lock()
gconn_list = []
connlock = threading.Lock()


def serverthread(IP, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, port))
    server.listen()
    while True:
        conn, addr = server.accept()
        print(addr[0] + " connected")
        # creates an individual thread for each machine that connects
        start_new_thread(msg_listen, (conn))


def msg_listen(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from the server for listening or connects to existing server
    if conn is None:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(IP, port)
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

        except Exception as e:
            print(e)
            continue

# TODO, implement clocks, rates, effective sending with conns, log files


def running_machine(rate):
    time.sleep(rate)
    clock = [0, 0, 0]
    while True:
        # check our message queue
        qlock.acquire(timeout=10)
        if len(msg_q) > 0:
            msg = msg_q.pop()
        else:
            msg = None
        qlock.release()

        # check connlist for updates
        connlock.acquire(timeout=10)
        conn_list = gconn_list
        connlock.release()

        time.sleep(rate)
        # act accordingly to the message
        if msg:
            clock = msg
        else:
            op = random.randint(1, 10)
            if op == 1 or op == 2:
                # NOT SURE if able to send message when separate thread connected
                # TODO figure out how to send to certain connections
                # maybe have to open connections in machine thread, then open listen threads with that connection passed in
                conn_list[op].send(clock[0])
            elif op == 3:
                for conn in conn_list:
                    conn.send(clock)
            else:
                clock[0] += 1


if __name__ == '__main__':
    this_IP = '10.250.189.78'
    thread_list = []
    # usage: python3 machine.py rate listenPORT targetIP targetPORT...

    # connect to all existing machines
    for i in range(4, sys.argv, 2):
        thread_list.append(threading.Thread(
            target=msg_listen, args=(None, sys.argv[i], sys.argv[i+1])))
        thread_list[i].start()

    # start machine thread
    threading.Thread(target=running_machine,
                     args=(10)).start()  # change rate as arg

    # then start its own thread to listen for future connections
    threading.Thread(target=serverthread, args=(this_IP, sys.argv[3])).start()
