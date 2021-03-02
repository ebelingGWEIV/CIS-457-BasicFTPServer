import socket
import ServerControlSocket
import concurrent.futures
import os


class FileServer(object):
    """
    @param server IP of the Command connection
    """
    def __init__(self, server, port):
        self.Run = False
        try:
            self.Create(server, port)
            if not os.path.isdir("./FileServer"):
                print("Creating FileServer directory")
                os.mkdir("./FileServer")
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
        self.welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcomeSocket.bind((server, controlPort))

    """
    @summary Listen for and handle connections from clients
    @param max_workers The max number of client connections possible (default = 10)
    """
    def ListenForConnections(self, max_workers=10):
        if(self.Run == False): return False

        self.welcomeSocket.listen() #start allowing connections to the server
        while self.Run == True:
            # print("waiting for connections")
            connection_socket, addr = self.welcomeSocket.accept()
            # print("got a connection")
            connectionInfo = (connection_socket, addr)
            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                executor.submit(ServerControlSocket.Controller, connectionInfo)

    def stopControlServer(self):
        self.Run = False
        self.__del__()

    def __del__(self):
        self.welcomeSocket.close()
        try:
            concurrent.futures.ThreadPoolExecutor.shutdown()
        except: #An exception would occur if there are
            print("No server connections running on shutdown")