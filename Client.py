import socket
import time

class Client():
    buffer_size = 4096
    """
    @param server IP of the Data connection
    """
    def __init__(self, ip):
        self.ip = ip
        self.commandConnected = False
        self.dataConnectionOpen = False
        self.welcomeConnected = False

    """
    " @summary Connects the client to the default port on the server
    " @param server
    " @param port
    """
    def Create(self, server, port = 1609, timeout = 50.0):
        self.fileServerIP = server
        self.welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcomeSocket.settimeout(timeout)
        self.welcomeSocket.connect((server, port))
        self.welcomeConnected = True
        self.timeout = timeout
        self.dataPort = ((port + 1111) % 65535) + 1

    """
    " @summary
    " @param
    " @param
    """
    def getCommandConnection(self, server, port):
        self.welcomeSocket.send(("CONNECT " + server + " " + str(port) + '$').encode('ascii'))
        time.sleep(1)
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.connect((server, port))
        self.commandConnected = True

    """
    " @summary
    " @param
    """
    def sendCommand(self, command):
        if(self.commandConnected == False):
            print("Control connection must be established first")
            return
        command = command + '$'
        self.controlSocket.send(str(command).encode('ascii'))

    """
    " @summary Ask the fileserver for a file by name. Opens a seperate data connection to receive the file on.
    " @param filename 
    """
    def RetreiveFile(self, filename):
        self.sendCommand("RETR " + filename + " " + str(self.dataPort))
        bytes = self.GetData()
        print("got file")
        file = open('./LocalStorage/'+filename, 'wb')
        file.write(bytes)
        file.close()

    """
    " @summary
    " @param
    """
    def StoreFile(self, filename):
        self.sendCommand("STOR " + filename + " " + str(self.dataPort))
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
        #todo implement file sending

    """
    " @summary Print a list of the files stored on the file server
    """
    def ListFiles(self):
        self.sendCommand("LIST " + str(self.dataPort))
        self.CreateDataSocketServer()
        files = bytes(self.GetData()).decode('ascii')
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
        self.dataSocket.bind((str(self.ip), int(self.dataPort)))
        self.dataSocket.listen()
        self.dataConnection, addr = self.dataSocket.accept()
        self.dataConnectionOpen = True

    """
    " @summary
    " @param 
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
        time.sleep(1)  # to ensure connection happens
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.connect((server, int(self.dataPort)))
        dataSocket.send(message) #Assummes that the data is less than the max size
        dataSocket.close()  # sends an EOF

    """
    " @summary
    """
    def CloseDataConnection(self):
        if(self.dataConnectionOpen == True):
            self.dataConnection.close()
            self.dataConnectionOpen = False
            self.dataSocket.close()

    """
    " @summary
    """
    def __del__(self):
        if(self.welcomeConnected == True):
            self.welcomeSocket.close()
        if(self.commandConnected == True):
            self.controlSocket.close()
        self.CloseDataConnection()
