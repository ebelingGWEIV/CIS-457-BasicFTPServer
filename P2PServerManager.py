import socket
import _thread
import os
import random
import P2PControlSocket


class ClientServerManager:
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

    def Create(self, server, controlPort=1609):
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
        if (self.Run == False): return False

        listening_socket.listen()  # start allowing connections to the server
        while self.Run == True:
            print("waiting for connections")
            connection_socket, addr = listening_socket.accept()
            print("got a connection")
            _thread.start_new_thread(self.onWelcome,
                                     (connection_socket,))  # A new thread is made for every connection to the server
        listening_socket.close()

    def onWelcome(self, connection_socket):
        newPort = random.randint(1024, 65535)
        # Verify that no control or data port will be duplicated
        while ((self.connectedPorts.__contains__(newPort)) or (
                self.connectedPorts.__contains__((newPort + 1) % 65535))):
            newPort = random.randint(1024, 65535)

        # Tell the client what port to connect to and wait for a connection
        controlSocket = self.Create(self.serverIP, newPort)
        controlSocket.settimeout(ClientServerManager.timeout)
        controlSocket.listen()
        connection_socket.send(("connect " + str(newPort)).encode('ascii'))
        newConnection, addr = controlSocket.accept()

        controlSocket.close()  # This is no longer needed, so it can be closed

        connectionInfo = (newConnection, addr)

        myControlSocket = P2PControlSocket.ClientControlSocket(connectionInfo, ClientServerManager.timeout,
                                                               self.serverIP)  # init the control server
        self.RunningControlSockets.append(myControlSocket)  # add it to the list of running servers
        myControlSocket.RunControlServer()  # start the control server

    def closeControlServer(self):
        self.Run = False
        for controlSocket in self.RunningControlSockets:
            controlSocket.__del__()

    def __del__(self):
        self.closeControlServer()
