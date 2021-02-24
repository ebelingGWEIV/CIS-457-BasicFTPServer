import socket
import time

class Client(object):
    """
    @param server IP of the Data connection
    """
    def __init__(self, server, port):
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.connect((server, port))
        print("created client")


    def createCommandConnection(self):
        self.controlSocket.send(("CONNECT 127.0.0.1 5612$").encode('ascii'))  # Sends port name
        time.sleep(2)
        print("asking for list")
        self.controlSocket.send(("list$").encode('ascii'))

    def __del__(self):
        self.controlSocket.close()
