import socket
import _thread
import os
import random

import ServerControlSocket


class FileServer(object):
    timeout = 50.0
    """
    " @summary Make the object, but don't start anything
    """
    def __init__(self):
        self.Run = False
        self.connectedPorts = []
        self.RunningControlSockets = []

    """
    " @summary Start the server
    " @param server IP of the server
    " @param port port to use for welcome connections
    """
    def Start(self, server, port):
        try:
            # The file server needs a directory to manage
            if not os.path.isdir("./FileServer"):
                print("Creating FileServer directory")
                os.mkdir("./FileServer")
            # Create and listen to the welcome socket the server will use
            welcomeSocket = self.Create(server, port)
            self.ListenForConnections(welcomeSocket)
        except:
            print("Server is shutting down")
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
    @param listening_socket The server socket clients will connect to
    """
    def ListenForConnections(self, listening_socket):
        if(self.Run == False): return False

        listening_socket.listen() #start allowing connections to the server
        while self.Run == True:
            print("waiting for connections")
            connection_socket, addr = listening_socket.accept()
            print("got a connection")
            myControlSocket = ServerControlSocket.Controller((connection_socket, addr), FileServer.timeout,
                                                             self.serverIP)  # init the control server
            self.RunningControlSockets.append(myControlSocket)  # add it to the list of running servers

            _thread.start_new_thread(myControlSocket.RunControlServer, ()) # A new thread is made for every connection to the server

        listening_socket.close()

    def closeControlServer(self):
        self.Run = False
        for controlSocket in self.RunningControlSockets:
            controlSocket.Quit()

    def __del__(self):
        self.closeControlServer()