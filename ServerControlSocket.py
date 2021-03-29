import socket
import FileRefList

class Controller():
    buffer_size = 4096
    FileRefs = FileRefList.FileRefs()  # The list of all files and their hosts declared as a static class property
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
        self.MyFiles = [] # empty list for files added by this host

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
            if command[0].lower() == "list":
                self.List(command[1])
                pass
            elif command[0].lower() == "quit":
                self.Quit()
                pass
            elif command[0].lower() == "add":
                self.AddFile(command)
                pass
            elif command[0].lower() == "search":
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
    " @summary Add a file to the list of file references
    " @param command The command recevied from the client
    "        fileName, hostName, file port, speed, confirmation port, description
    """
    def AddFile(self, command):
        fileName = command[1]
        hostName = command[2]
        portNum = command[3]
        speed = command[4]
        confirmPort = command[5]
        description = command[6:]

        descriptor = ""
        for word in description:
            descriptor = descriptor + " " + word

        try:
            fileTup = (fileName, hostName, portNum, speed)

            print("adding file " + descriptor)
            self.MyFiles.append(hostName)  # Add to the list of my files added
            Controller.FileRefs.add(descriptor, fileTup)  # Add to the list of all files registered

            self.SendData(("file added\n").encode('ascii'), confirmPort)
        except:
            print("error adding file")
            self.SendData(("could not add\n").encode('ascii'), confirmPort)

    """
    " @summary Send information about a host through the data port
    " @param hostInfo The name and data port of the host server as a HostInfo object
    " @param dataPort The port to send the host info on 
    """
    def Search(self, keyword, dataPort):
        hostInfo = Controller.FileRefs.search(keyword)
        if len(hostInfo) == 0:
            hostInfo.append(FileRefList.HostInfo("", "", "", ""))
        message = ""
        for host in hostInfo:
            message = host.FileName + ", " + host.HostName + " " + str(host.PortNum) + "\n"
        self.SendData((message).encode('ascii'), dataPort)

    """
    " @summary Handle the client command to return a directory list of the FileServer
    " @param dataPort The name of the port to send the list over
    """
    def List(self, dataPort):
        try:
            message = ""
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
        self.dataSeverOpen = False
        self.CloseDataConnection()
        Controller.FileRefs.remove(self.MyFiles)

    """
    " @summary Safely delete using the Quit method
    """
    def __del__(self):
        self.Quit()