import socket
import time
import os

class Client():
    buffer_size = 4096 #I put this here on accident, but it made me realized that classes can have properties. Now I wish it wasn't nearly done with the project, because there are things I would change.
    """
    @param server IP of the Data connection
    """
    def __init__(self, ip):
        # These are probably all things that should be Client properties, but it's too late now. This is my first python
        # project, so I had a lot to learn.
        self.ip = ip
        self.commandConnected = False
        self.dataConnectionOpen = False
        self.welcomeConnected = False
        self.dataPort = 0
        if not os.path.isdir("./LocalStorage"):
            print("Creating LocalStorage directory")
            os.mkdir("./LocalStorage")

    """
    " Connect to the server and wait for a message with the new port to connect the control socket to.
    " @param server IP of the file server
    " @param port Port for control connection on the file server
    " @param timeout Set the timeout for the client's connections
    """
    def connectToServer(self, server, port = 1609, timeout = 50.0):
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
    " @summary Run the store file command. Loads a file from disk as bytes and sends it to the file server over a new data connection.
    " @param name of the file in ./LocalStorage
    """
    def StoreFile(self, filename):
        self.sendCommand("STOR " + filename + " " + str(self.dataPort))
        try:
            file = open('./LocalStorage/' + filename, 'rb')
            newChar = file.read(1)
            data = bytes(''.encode('ascii'))
            while newChar:
                data = data + newChar
                newChar = file.read(Client.buffer_size)
                if not newChar:
                    break
            self.ConnectAndSendData(self.fileServerIP, data)
            file.close()
        except:
            print("Error occurred while sending file to server")


    """
    " @summary Print a list of the files stored on the file server
    """
    def ListFiles(self):
        self.sendCommand("LIST " + str(self.dataPort))
        files = bytes(self.GetData(self.dataPort)).decode('ascii')
        print("Files stored on server are: ")
        print(files)
        self.CloseDataConnection()

    """
    " @summary Send a quit message to the fileserver, and close this client.
    """
    def Quit(self):
        if(self.commandConnected == True):
            self.sendCommand("quit")
        self.__del__()

    """
    " @summary Create the data socket as the server and wait for a connection from the fileserver.
    """
    def CreateDataSocketServer(self):
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.settimeout(self.timeout)
        self.dataSocket.bind((str(self.ip), int(self.dataPort)))
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
        if(self.commandConnected == True):
            self.controlSocket.close()
        self.CloseDataConnection()
