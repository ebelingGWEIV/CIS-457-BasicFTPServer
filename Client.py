import socket
import time

class Client(object):
    """
    @param server IP of the Data connection
    """
    def __init__(self, server, port):
        self.fileServerIP = server
        self.initialSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.initialSocket.connect((server, port))
        self.commandConnected = False
        print("created client")


    def createCommandConnection(self, server, port = 1609):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((server, port))
        self.serverSocket.listen()
        self.initialSocket.send(("CONNECT " + server + " " + port + "$").encode('ascii'))  # Sends port name
        self.command_connection, addr = self.server_socket.accept()
        self.commandConnected = True

    def sendCommand(self, command):
        if(self.commandConnected == False):
            print("must be connected first. Connecting using default settings")
            self.createCommandConnection(self.fileServerIP)
        self.command_connection.send(command)

    def RetreiveFile(self, filename):
        self.sendCommand("RETR " + filename)
        #todo implement file receving

    def StoreFile(self, filename):
        self.sendCommand("STOR " + filename)
        #todo implement file sending

    def ListFiles(self):
        self.sendCommand("LIST")

    def Quit(self):
        self.sendCommand("quit")
        self.__del__(self)

    def __del__(self):
        self.initialSocket.close()
