import socket

class ClientControlSocket:
    buffer_size = 4096
    timeout = 10.0

    def __init__(self, connectionInfo, timeout = 50.0, myIp = "localhost"):
        self.controlCon = connectionInfo[0]
        # myClient = connectionInfo[1]
        self.ip = connectionInfo[1][0]
        self.myPort = connectionInfo[1][1]
        self.myIP = myIp
        self.timeout = timeout
        self.Run = True
        self.dataConnectionOpen = False
        self.dataSeverOpen = False
        self.MyFiles = []  # empty list for files added by this host
        pass

    """
    " @summary Receive messages from the client and send them to the message handler on a separate thread.
    """
    def RunControlServer(self):
        while(self.Run == True):
            try:
                message = self.controlCon.recv(ClientControlSocket.buffer_size).decode('ascii')  # we assume that
                self.HandleMessage(message)
            except ConnectionResetError as ex:
                print("Client closed forcibly. Server on port " + str(self.myPort) + " is closing")
                self.Quit()

    """
    " @summary Handle all expected commands from the client
    " @param message The full message received from the client as a string
    """
    def HandleMessage(self, message):
        try:
            print("P2P: " + message)
            command = str(message).split()
            if command[0].lower() == "retr":
                self.ReturnFile(command[1], command[2])
                print("file returned: " + command[1])
                pass
            elif command[0].lower() == "quit":
                self.Quit()
            else:
                print("Command not supported")
                pass
        except:
            print("Client sent bad request that could not be responded to on the data port. Closing this connection")
            self.Quit()

    """
    " @summary Handle the client command to return a file
    " @param filename The name of the file to send the client
    " @param dataPort The name of the port to send the file over
    """
    def ReturnFile(self, filename, dataPort):
        try:
            file = open('./FileServer/'+filename, 'rb')
            newChar = file.read(1)
            data = bytes(''.encode('ascii'))
            while newChar:
                data = data + newChar
                newChar = file.read(ClientControlSocket.buffer_size)
                if not newChar:
                    break
            self.SendData(data, dataPort)
            file.close()
        except:
                print("Client sent bad request")
                self.SendBlankData(dataPort)

    """
    " @summary Send data to the client
    " @param message The pre-constructed 'message' to send
    " @param dataPort The port to send data over
    """
    def SendData(self, message, dataPort):
        # time.sleep(1) #to ensure the client is listening
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.settimeout(self.timeout)
        dataSocket.connect((self.ip, int(dataPort)))
        dataSocket.send(message)
        dataSocket.close() #sends an EOF

    """
    " @summary Sends an EOF message
    " @param dataPort The port to send data over
    """
    def SendBlankData(self, dataPort):
        data = bytes(''.encode('ascii'))
        self.SendData(data, dataPort)

    """
    " @summary Create the data socket as the server and wait for a connection from the fileserver.
    " @param ip The IP of the file server
    " @param dataPort The port to bind to
    """
    def CreateDataSocket(self, ip, dataPort):
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.bind((str(ip), int(dataPort)))
        self.dataSocket.listen()
        self.dataConnection, addr = self.dataSocket.accept()
        self.dataSocket.close()
        self.dataConnectionOpen = True


    """
    " @summary If the data connection is currently open, close the connections and the socket.
    """
    def CloseDataConnection(self):
        if(self.dataConnectionOpen == True):
            self.dataConnection.close()
            self.dataConnectionOpen = False
            self.dataSocket.close()


    """
    " @summary Reset flags and close connection to the client.
    " @note The socket is closed in the FileServerManager
    """
    def Quit(self):
        self.Run = False
        self.dataSeverOpen = False
        self.CloseDataConnection()

    """
    " @summary Safely delete using the Quit method
    """
    def __del__(self):
        self.Quit()