import socket
import _thread
import concurrent.futures
import os
import random

import ServerControlSocket


class FileServer(object):
    """
    @param server IP of the Command connection
    """
    def __init__(self, server, port):
        self.Run = False
        self.connectedPorts = []
        self.RunningControlSockets = []
        try:
            if not os.path.isdir("./FileServer"):
                print("Creating FileServer directory")
                os.mkdir("./FileServer")
            welcomeSocket = self.Create(server, port)
            self.ListenForConnections(welcomeSocket)
        except:
            print("Failed to start file server")
            self.__del__()


    """
    @summary Bind server to IP and port number. Does not begin accepting client connections
    @param server IP for the server
    @param controlPort The default port for the server
    """
    def Create(self, server, controlPort = 1609):
        self.Run = True
        self.serverIP = server
        welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcomeSocket.bind((server, controlPort))
        self.connectedPorts.append(controlPort)
        return welcomeSocket

    """
    @summary Listen for and handle connections from clients
    @param max_workers The max number of client connections possible (default = 10)
    """
    def ListenForConnections(self, listening_socket, max_workers=10):
        if(self.Run == False): return False

        listening_socket.listen() #start allowing connections to the server
        while self.Run == True:
            print("waiting for connections")
            connection_socket, addr = listening_socket.accept()
            print("got a connection")
            _thread.start_new_thread(self.onWelcome, (connection_socket,))

        listening_socket.close()


    def onWelcome(self, connection_socket):
        newPort = random.randint(1024, 65535)
        #Verify that no control or data port will be duplicated
        while((self.connectedPorts.__contains__(newPort) ) or (self.connectedPorts.__contains__((newPort + 1) % 65535))):
            newPort = random.randint(1024, 65535)
        controlSocket = self.Create(self.serverIP, newPort)

        controlSocket.listen()
        connection_socket.send(("connect " + str(newPort)).encode('ascii'))
        newConnection, addr = controlSocket.accept()

        controlSocket.close() #This is no longer needed

        connectionInfo = (newConnection, addr)

        myControlSocket = ServerControlSocket.Controller(connectionInfo) # init the control server
        self.RunningControlSockets.append(myControlSocket) # add it to the list of running servers
        myControlSocket.RunControlServer() # start the control server

    def stopControlServer(self):
        self.Run = False
        self.__del__()

    def __del__(self):
        for socket in self.RunningControlSockets:
            socket.Quit()
        try:
            concurrent.futures.ThreadPoolExecutor.shutdown()
        except: #An exception would occur if there are
            print("No server connections running on shutdown")