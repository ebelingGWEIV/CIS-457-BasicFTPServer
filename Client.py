import socket
import _thread
import time

class Client():
    """
    @param server IP of the Data connection
    """
    def __init__(self):
        self.commandConnected = False

    """
    @summary Connects the client to the default port on the server
    @param server
    @param port
    """
    def Create(self, server, port = 1609):
        Client.fileServerIP = server
        self.welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcomeSocket.connect((server, port))
        self.dataPort = ((port + 1111) % 65535) + 1


    def getCommandConnection(self, server, port):
        self.welcomeSocket.send(("CONNECT " + server + " " + str(port) + '$').encode('ascii'))
        time.sleep(1)
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.connect((server, port))
        self.commandConnected = True

    def sendCommand(self, command):
        if(self.commandConnected == False):
            print("must be connected first. Connecting using default settings")
            self.getCommandConnection(self.fileServerIP)
        print("sending " + command)
        command = command + '$'
        self.controlSocket.send(str(command).encode('ascii'))

    def RetreiveFile(self, filename):
        self.sendCommand("RETR " + filename + " " + self.dataPort)
        #todo implement file receving

    def StoreFile(self, filename):

        self.sendCommand("STOR " + filename + " " + self.dataPort)
        #todo implement file sending

    def ListFiles(self):
        self.sendCommand("LIST " + self.dataPort)

    def Quit(self):
        if(self.commandConnected == True):
            self.sendCommand("quit")
        self.__del__()

    def __del__(self):
        self.welcomeSocket.close()
        if(self.commandConnected == True):
            self.controlSocket.close()
