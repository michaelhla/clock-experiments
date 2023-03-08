import socket
import select
import sys
import threading
from _thread import *
import random
import time
import datetime

msg_q = []
qlock = threading.Lock()
gconn_list = []
connlock = threading.Lock()
machine_ID = -1

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



def running_machine(rate):
    # logical clock starts at 0
    clock = 0    
    # name log file, with ind enumerating the file
    name = "log_"+str(machine_ID)+".5"+".txt"
    with open(name, "w") as f:
        f.write("LOG_"+str(machine_ID)+".5"+"\n")
        f.write("Rate: " + str(rate)+"\n")
    # ensures connections are fully initialized before starting clock cycles
    full_conn = False
    while full_conn == False:
        connlock.acquire(timeout=10)
        if len(gconn_list) == 2:
            full_conn = True
            print(gconn_list)
        connlock.release()

    while True:
        time.sleep(1/rate)
        msg = None
        q_len = 0
        # check our message queue
        qlock.acquire(timeout=10)
        if len(msg_q) > 0:
            msg = msg_q.pop()
            # extract "current" queue length
            q_len = len(msg_q)
        qlock.release()
        if msg:
            sender = msg[0]
            TS = int(msg[1:].decode())
            #update logical clock
            clock = max(TS, clock)
            clock += 1
            #automatically opens and closes for file safety; in a mode to append instead of overwrite file
            with open(name, "a") as f:
                f.write("RecMsg,"+str(datetime.datetime.now())+","+str(q_len)+","+str(clock)+"\n")
        else:
            op = random.randint(1, 10)
            if op == 1 or op == 2:
                connlock.acquire(timeout=10)
                if len(gconn_list) > 1:
                    #sends message to desired connection
                    conn = gconn_list[op-1]
                    sender = machine_ID.to_bytes(1, "big")
                    clock_val = str(clock).encode()
                    conn.sendall(sender + clock_val)
                connlock.release()
                clock+=1
                with open(name, "a") as f:
                    f.write("SentMsg,"+str(datetime.datetime.now())+","+str(clock)+"\n")
            elif op == 3:
                connlock.acquire(timeout=10)
                #sends double message
                for conn in gconn_list:
                    sender = machine_ID.to_bytes(1, "big")
                    clock_val = str(clock).encode()
                    conn.sendall(sender + clock_val)
                connlock.release()
                clock+=1
                with open(name, "a") as f:
                    f.write("SentDoubMsg,"+str(datetime.datetime.now())+","+str(clock)+"\n")
            else:
                #internal event with clock update
                clock+=1
                with open(name, "a") as f:
                    f.write("IntEvent,"+str(datetime.datetime.now())+","+str(clock)+"\n")



if __name__ == '__main__':
    this_IP = '10.250.55.253'
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
    print(rate)
    threading.Thread(target=running_machine,
                     args=(rate,)).start()  # change rate as arg

    # then start its own thread to listen for future connections
    threading.Thread(target=serverthread, args=(
        this_IP, int(sys.argv[2]))).start()
    print("init complete")

# in succession, run:
# python3 machine.py 1 8080
# python3 machine.py 2 8081 10.250.55.253 8080
# python3 machine.py 3 8082 10.250.55.253 8081 10.250.55.253 8080
