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
machine_ID = -1

#Hello

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


def msg_listen(conn, IP=None, port=None):
    # this is where a machine will listen when it recognizes a connection
    # either gets a conn from machine server for listening or connects to existing server
    if conn is None:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((IP, port))

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
    clock = [0, 0, 0]
    while True:
        time.sleep(1/rate)

        # check our message queue
        qlock.acquire(timeout=10)
        if len(msg_q) > 0:
            msg = msg_q.pop()
        else:
            msg = None
        qlock.release()

        time.sleep(1/rate)
        # act accordingly to the message
        if msg:
            sent = msg[0]
            clock[sent] = int(msg[1:].decode())
        else:
            op = random.randint(1, 10)
            if op == 1 or op == 2:
                # NOT SURE if able to send message when separate thread connected
                # TODO figure out how to send to certain connections
                # maybe have to open connections in machine thread, then open listen threads with that connection passed in

                connlock.acquire(timeout=10)
                if len(gconn_list) > 1:
                    conn = gconn_list[op-1]
                    sender = machine_ID.to_bytes(1, "big")
                    clock_val = str(clock[machine_ID]).encode()
                    conn.send(sender + clock_val)
                connlock.release()
            elif op == 3:
                connlock.acquire(timeout=10)
                for conn in gconn_list:
                    sender = machine_ID.to_bytes(1, "big")
                    clock_val = str(clock[machine_ID]).encode()
                    conn.send(sender + clock_val)
                connlock.release()

            else:
                clock[machine_ID] += 1
            print(clock)


if __name__ == '__main__':
    this_IP = '10.250.189.78'
    thread_list = []
    # usage: python3 machine.py machine_ID listenPORT targetIP targetPORT...
    # start machines in sequence
    machine_ID = int(sys.argv[1])

    # connect to all existing machines
    if len(sys.argv) > 3:
        count = 0
        for i in range(3, len(sys.argv), 2):
            thread_list.append(threading.Thread(
                target=msg_listen, args=(None, sys.argv[i], int(sys.argv[i+1]))))
            thread_list[count].start()
            count += 1

    # start machine thread
    rate = random.randint(1, 6)
    threading.Thread(target=running_machine,
                     args=(rate,)).start()  # change rate as arg

    # then start its own thread to listen for future connections
    threading.Thread(target=serverthread, args=(
        this_IP, int(sys.argv[2]))).start()
    print("init complete")


# python3 machine.py 10 8082 10.250.189.78 8080 10.250.189.78 8081 (last machine start with my IP)
