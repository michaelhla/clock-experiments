from _thread import *
import time
import unittest
import subprocess
from unittest.mock import patch
import psutil

# Tests for basic occurrences of messages in log books for three concurrent processes


class Test(unittest.TestCase):

    def init(self):
        self.machine1 = subprocess.Popen(
            ["python3", "test_machine.py", "1", "8080"], stdout=subprocess.PIPE)
        time.sleep(0.1)
        self.machine2 = subprocess.Popen(
            ["python3", "test_machine.py", "2", "8081", "10.250.189.78", "8080"], stdout=subprocess.PIPE)
        time.sleep(0.1)
        self.machine3 = subprocess.Popen(["python3", "test_machine.py", "3", "8082",
                                         "10.250.189.78", "8080", "10.250.189.78", "8081"], stdout=subprocess.PIPE)

    def end(self):
        self.machine1.terminate()
        self.machine2.terminate()
        self.machine3.terminate()

    def test(self):
        self.init()
        time.sleep(10)

        pid = self.machine1.pid

        # Find all child processes of the subprocess
        parent_process = psutil.Process(pid)
        child_processes = parent_process.children(recursive=True)

        # Kill all child processes
        for child in child_processes:
            child.kill()

        # Kill the subprocess itself
        self.machine1.kill()

        pid = self.machine2.pid

        # Find all child processes of the subprocess
        parent_process = psutil.Process(pid)
        child_processes = parent_process.children(recursive=True)

        # Kill all child processes
        for child in child_processes:
            child.kill()

        # Kill the subprocess itself
        self.machine2.kill()

        pid = self.machine3.pid

        # Find all child processes of the subprocess
        parent_process = psutil.Process(pid)
        child_processes = parent_process.children(recursive=True)

        # Kill all child processes
        for child in child_processes:
            child.kill()

        # Kill the subprocess itself
        self.machine3.kill()

        self.machine1.terminate()
        self.machine2.terminate()
        self.machine3.terminate()

        self.machine1.wait()
        self.machine2.wait()
        self.machine3.wait()

        with open("log_1.txt", "r") as f:
            log = f.read()
            self.assertTrue(
                "IntEvent" in log or "RecMsg" in log or "SentMsg" in log or "SentDoubMsg" in log)
            f.close()
        with open("log_2.txt", "r") as f:
            log = f.read()
            self.assertTrue(
                "IntEvent" in log or "RecMsg" in log or "SentMsg" in log or "SentDoubMsg" in log)
            f.close()
        with open("log_3.txt", "r") as f:
            log = f.read()
            self.assertTrue(
                "IntEvent" in log or "RecMsg" in log or "SentMsg" in log or "SentDoubMsg" in log)
            f.close()


if __name__ == '__main__':
    unittest.main()
