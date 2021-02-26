import socket
import ServerControlSocket
import concurrent.futures


class FileServer(object):
    """
    @param server IP of the Command connection
    """
    def __init__(self, server, controlPort):
        self.Run = True
        self.serverIP = server
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((server, controlPort))
        print("created server")

    def ListenForConnections(self, buffer_size, max_workers=10):
        self.serverSocket.listen() #start allowing connections to the server
        print("waiting for connections")

        connection_socket, addr = self.serverSocket.accept()
        print("got a connection from: " + addr)
        connectionInfo = (connection_socket, addr)
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            executor.submit(ServerControlSocket.Controller, connectionInfo)

    def stopControlServer(self):
        self.__del__(self)



    def __del__(self):
        self.serverSocket.close()
        concurrent.futures.ThreadPoolExecutor.shutdown()