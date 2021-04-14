import socket
import FileRefList

class Controller():
    buffer_size = 4096
    FileRefs = FileRefList.FileRefs()  # The list of all files and their hosts declared as a static class property
    Users = {} # Username, (host, speed)
    """
    " @summary
    " @param
    """
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
        self.registered = False
        self.clientSpeed = ""
        self.clientUserName = ""

    def SetupUser(self, name, speed, confirmPort):
        if not (name in Controller.Users):
            self.clientUserName = name
            self.clientSpeed = speed
            Controller.Users[name] = (str(self.ip), str(speed))
            self.registered = True
            self.SendData(("User is registered").encode('ascii'), confirmPort)
            pass
        else:
            self.SendData(("User name is taken").encode('ascii'), confirmPort)

    """
    " @summary Receive messages from the client and send them to the message handler on a separate thread.
    """
    def RunControlServer(self):

        while(self.Run == True):
            try:
                message = self.controlCon.recv(Controller.buffer_size).decode('ascii')  # we assume that
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
            command = str(message).split()
            if len(command) == 0: return
            print(f'user: {self.clientUserName} - {command}')
            if command[0].lower() == "reg":
                self.SetupUser(command[1], command[2], command[3])
                return

            elif command[0].lower() == "list":
                if self.registered is False:
                    self.NotRegistered(command[1])
                    pass
                else:
                    self.List(command[1])
                pass
            elif command[0].lower() == "quit":
                if self.registered is False:
                    print("User left before registering")
                    pass
                else:
                    self.Quit()
                    pass
            elif command[0].lower() == "add":
                if self.registered is False:
                    self.NotRegistered(command[3])
                    pass
                else:
                    self.AddFile(command)
                    pass
            elif command[0].lower() == "search":
                if self.registered is False:
                    self.NotRegistered(command[2])
                    pass
                else:
                    print("returning info search with keyword " + command[1])
                    self.Search(command[1], command[2])
                    pass
            else:
                print("Command not supported")
                pass
        except ConnectionRefusedError as e:
            print("Connection over data port was refused. Cannot communicate, closing connection")
            self.Quit()
        except Exception as e:
            print(e)
            print("Client sent bad request that could not be responded to on the data port.")

    """
    " @Summary If a user gives a command without registering, tell them so
    " @param dataPort the port to return on
    """
    def NotRegistered(self, dataPort):
        print("User is not registered")
        self.SendData("User not registered".encode('ascii'), dataPort)

    """
    " @summary Add a file to the list of file references
    " @param command The command recevied from the client
    "        fileName, hostName, file port, speed, confirmation port, description
    """
    def AddFile(self, command):
        fileName = command[1]
        hostName = self.ip
        portNum = command[2]
        speed = self.clientSpeed
        confirmPort = command[3]
        description = command[4:]

        descriptor = ""
        for word in description:
            descriptor = descriptor + " " + word

        fileTup = (fileName, hostName, portNum, speed, self.clientUserName)

        print("adding file " + descriptor)
        Controller.FileRefs.add(descriptor, fileTup)  # Add to the list of all files registered

        self.SendData(("file added").encode('ascii'), confirmPort)

    """
    " @summary Send information about a host through the data port
    " @param hostInfo The name and data port of the host server as a HostInfo object
    " @param dataPort The port to send the host info on 
    """
    def Search(self, keyword, dataPort):
        hostInfo = Controller.FileRefs.search(keyword)
        if len(hostInfo) == 0:
            hostInfo.append(FileRefList.HostInfo("", "", "", "", ""))
        message = ""
        for host in hostInfo:
            message = host.Speed + ", " + host.HostName + "/" + str(host.PortNum) + ", " + host.FileName + " " + "\n"
        self.SendData(message.encode('ascii'), dataPort)

    """
    " @summary Handle the client command to return a directory list of the FileServer
    " @param dataPort The name of the port to send the list over
    """
    def List(self, dataPort):
        try:
            list = Controller.FileRefs.list()
            message = ""
            if len(list) > 0:
                for entry in list:
                    message = message + entry[0] + ", " + entry[1] + ", " + entry[2] + " " + entry[3] + "\n"
            self.SendData((message).encode('ascii'), dataPort)
        except:
            print("error getting file list")
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
    " @summary Open a data socket as the server and collect data from the client until an EOF is received.
    " @param dataPort The port to collect data from
    """
    def GetData(self, dataPort, buf_size = buffer_size):
        self.CreateDataSocket(str(self.myIP), dataPort)
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
        self.dataConnectionOpen = False
        self.dataSeverOpen = False
        self.registered = False
        self.CloseDataConnection()

        Controller.FileRefs.remove(self.clientUserName)
        try:
            Controller.Users.pop(self.clientUserName)
        except:
            pass  # for cases where user closes and server is forced closed but server wasn't deconstructed yet

    """
    " @summary Safely delete using the Quit method
    """
    def __del__(self):
        self.Quit()