import socket
import os
import random
import P2PServerManager
import _thread


class Client:
    buffer_size = 4096
    """
    @param server IP of the Data connection
    """
    def __init__(self, ip, makeServer = True):
        self.myIP = ip
        self.commandConnected = False
        self.dataConnectionOpen = False
        self.welcomeConnected = False
        self.serverRunning = makeServer
        self.dataPort = 0
        self.myServerPort = self.randPort()
        if not os.path.isdir("./LocalStorage"):
            print("Creating LocalStorage directory")
            os.mkdir("./LocalStorage")

        if makeServer:
            self.myServer = P2PServerManager.ClientServerManager()
            _thread.start_new_thread(self.myServer.Start, (self.myIP, self.myServerPort, ))
        pass

    """
    " Get a valid port number
    " @return a random number between 1024 and 65535
    """
    def randPort(self):
        return random.randint(1024, 65535)
    """
    " Connect to the server and wait for a message with the new port to connect the control socket to.
    " @param server IP of the file server
    " @param port Port for control connection on the file server
    " @param timeout Set the timeout for the client's connections
    """
    def connectToServer(self, server, port = 1609, timeout = 10.0):
        if(self.commandConnected == True):
            print("Cannot connect to more than one server")
            return

        self.timeout = timeout
        self.fileServerIP = server
        welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcomeSocket.settimeout(self.timeout)
        welcomeSocket.connect((self.fileServerIP, int(port)))

        data = welcomeSocket.recv(Client.buffer_size).decode('ascii')
        message = data.split()
        welcomeSocket.close()

        if(message[0].lower() == str('connect')):
            self.createControlConnection(message[1])
            if self.commandConnected:
                print("Connected to server")
                return

        print("Could not connect to server")

    """
    " @summary Connect the control socket to the file server
    " @param port Port for control connection on the file server
    """
    def createControlConnection(self, port):
        self.dataPort = ((int(port) + 1) % 65535)
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.settimeout(self.timeout)
        self.controlSocket.connect((self.fileServerIP, int(port)))
        self.commandConnected = True

    """
    " @summary Send commands to the file server through TCP
    " @param command for the server
    """
    def sendCommand(self, command):
        if(self.commandConnected == False):
            print("Control connection must be established first")
            return
        self.controlSocket.send(str(command).encode('ascii'))

    """
    " @Summary Send a search request to the file server
    " @param keyword Keyword to use for search
    """
    def Search(self, keyword):
        self.sendCommand("SEARCH " + keyword + " " + str(self.dataPort))
        files = bytes(self.GetData(self.dataPort)).decode('ascii')
        print("Search results:\n")
        print(files)
        self.CloseDataConnection()

    """
    " @Summary Creates a new client to get the requested file from a peer
    " @param host ip of file's host
    " @param port port to get file over
    " @param filename name of requested file
    """
    def Get(self, filename, host, port):
        try:
            # start a new client
            print("starting")
            tmpClient = Client(self.myIP, False)
            # connect to the client-server
            print("connecting")
            tmpClient.connectToServer(host, port)
            print("connected " + str(self.commandConnected))
            # call its RetrieveFile command
            print("getting")
            tmpClient.RetreiveFile(filename)
            # close the client
            print("quitting")
            tmpClient.Quit()
        except:
            print("Could not get file \"" + filename + "\" from host \"" + host + "\" on port " + port)

    """
    " @summary Ask the fileserver for a file by name. Opens a seperate data connection to receive the file on.
    " @param filename 
    """
    def RetreiveFile(self, filename):
        self.sendCommand("RETR " + filename + " " + str(self.dataPort))
        bytes = self.GetData(self.dataPort)
        print("got file")
        file = open('./LocalStorage/'+filename, 'wb')
        file.write(bytes)
        file.close()

    """
    " @summary Print a list of the files stored on the file server
    """
    def ListFiles(self):
        self.sendCommand("LIST " + str(self.dataPort))
        files = bytes(self.GetData(self.dataPort)).decode('ascii')
        print("Available Files:\n")
        print(files)
        self.CloseDataConnection()

    """
    " @summary Print a list of the files stored on the file server
    """
    def Register(self, name, speed):
        self.sendCommand("REG " + str(name) + " " + str(speed) + " " + str(self.dataPort))
        confirm = bytes(self.GetData(self.dataPort)).decode('ascii')
        print(confirm)
        self.CloseDataConnection()

    """
    " @summary Add a file description to the server
    " @param file Name of the stored file
    " @param description A description of the file used for keyword searches
    " @param speed The type of connection or the upload speed of it
    """
    def AddFile(self, file, description):
        try:
            # Use the data port number for the client's server port. There will be no problems because the client's ip and port will be different from the ControlServer's
            descriptor = ""
            for word in description:
                descriptor = descriptor + " " + word

            command = "ADD " + file + " " + str(self.myServerPort) + " " + str(self.dataPort) + descriptor
            self.sendCommand(command)
            confirmation = bytes(self.GetData(self.dataPort)).decode('ascii')
            print(confirmation)
        except:
            print(f'could not add file {file}')

        self.CloseDataConnection()


    """
    " @summary Send a quit message to the fileserver, and closes this client.
    """
    def Quit(self):
        if(self.commandConnected == True):
            self.sendCommand("quit")
            self.controlSocket.close()
            self.commandConnected = False
        self.CloseDataConnection()
        if self.serverRunning:
            self.serverRunning = False
            self.myServer.closeControlServer()
            self.myServer.__del__()

    """
    " @summary Create the data socket as the server and wait for a connection from the fileserver.
    """
    def CreateDataSocketServer(self):
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.settimeout(self.timeout)
        self.dataSocket.bind((str(self.myIP), int(self.dataPort)))
        self.dataSocket.listen()
        self.dataConnection, addr = self.dataSocket.accept()
        self.dataConnectionOpen = True

    """
    " @summary Creates the data socket as the server and waits until an EOF is received
    " @param buf_size The number of bytes to receive at one time
    """
    def GetData(self, buf_size = buffer_size):
        self.CreateDataSocketServer() #Make a new datasocket
        message = bytes(''.encode('ascii'))
        while 1:
            data = self.dataConnection.recv(buf_size)
            if not data:
                break
            if len(data) > 0:
                message = message + data

        self.CloseDataConnection() #Close the datasocket
        return message

    """
    " @summary Connects to the data socket opened by the file server. Closes the connection after all data has been sent.
    " @param All of the data that should be sent
    """
    def ConnectAndSendData(self, server, message):
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.settimeout(self.timeout)
        try:
            self.dataSocket.connect((server, int(self.dataPort)))
            self.dataConnectionOpen = True
            self.dataSocket.send(message) #Assummes that the data is less than the max size
        except:
            print("Error occurred while sending data to the server")
        finally:
            self.CloseDataConnection()

    """
    " @summary Close the data socket
    """
    def CloseDataConnection(self):
        if(self.dataConnectionOpen == True):
            self.dataConnection.close()
            self.dataConnectionOpen = False
            self.dataSocket.close()

    """
    " @summary Close the control and data sockets.
    """
    def __del__(self):
        self.Quit()
