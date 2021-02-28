import socket
import concurrent.futures
import os
import time

class Controller():
    buffer_size = 4096

    """
    " @summary
    " @param
    """
    def __init__(self, connectionInfo, timeout = 50.0):
        self.welcomeConn = connectionInfo[0]
        # myClient = connectionInfo[1]
        self.ip = connectionInfo[1][0]
        self.connected = False
        self.Run = True
        self.dataConnectionOpen = False
        self.dataSeverOpen = False
        self.StartControlServer()
        self.listenForCommands()

    """
    " @summary
    """
    def StartControlServer(self):
        while(self.connected == False):
            message = self.welcomeConn.recv(Controller.buffer_size).decode('ascii')  # we assume that
            self.HandleMessage(message)

    """
    " @summary
    """
    def listenForCommands(self):
        while self.Run:
            message = self.controlConnection.recv(Controller.buffer_size).decode('ascii') #we assume that
            self.HandleMessage(message)

    """
    " @summary
    " @param
    " @param
    """
    def HandleMessage(self, message, max_workers=10):
        if message.endswith('$'):
            print("server got " + message)
            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                executor.submit(self.onCommand, message[:len(message) - 1])
            message = ''

    """
    " @summary
    " @param
    " @return True to 
    """
    def onCommand(self, message):
        command = str(message).split()
        if command[0].lower() == 'connect' and self.connected == False:
            self.Connect(command)
            pass
        elif command[0].lower() == "list":
            self.List(command[1])
            pass
        elif command[0].lower() == "retr":
            self.Retreive(command[1], command[2])
            pass
        elif command[0].lower() == "stor":
            self.StoreFile(command[1], command[2])
            pass
        elif command[0].lower() == "quit":
            self.Quit()
        pass

    """
    " @summary
    " @param
    """
    def Connect(self, command):
        self.controlServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlServer.bind((command[1], int(command[2])))
        self.controlServer.listen()
        self.controlConnection, self.clientAddr = self.controlServer.accept()
        self.connected = True

    """
    " @summary
    " @param
    """
    def List(self, dataPort):
        arr = os.listdir('./FileServer')
        message = ""
        for file in arr:
            message = message + file + '\n'
        self.SendData((message).encode('ascii'), dataPort)

    """
    " @summary
    " @param
    " @param
    """
    def Retreive(self, filename, dataPort):
        file = open('./FileServer/'+filename, 'rb')
        newChar = file.read(1)
        data = bytes(''.encode('ascii'))
        while newChar:
            data = data + newChar
            newChar = file.read(Controller.buffer_size)
            if not newChar:
                break
        self.SendData(data, dataPort)
        file.close()
        pass

    """
    "
    """
    def StoreFile(self, filename, dataPort):
        bytes = self.GetData(dataPort)
        print("got file")
        file = open('./FileServer/' + filename, 'wb')
        file.write(bytes)
        file.close()

    """
    " @summary
    " @param
    " @param
    """
    def SendData(self, message, dataPort):
        time.sleep(1) #to ensure connection happens
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.connect((self.clientAddr[0], int(dataPort)))
        dataSocket.send(message)
        dataSocket.close() #sends an EOF

    """
    " @summary Create the data socket as the server and wait for a connection from the fileserver.
    """
    def CreateDataSocket(self, ip, dataPort):
        print("making data socket " + ip + " " + dataPort)
        self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSocket.bind((str(ip), int(dataPort)))
        self.dataSocket.listen()
        self.dataSeverOpen = True
        self.dataConnection, addr = self.dataSocket.accept()
        self.dataConnectionOpen = True

    """
    " @summary
    " @param
    """
    def GetData(self, dataPort, buf_size = buffer_size):
        self.CreateDataSocket("localhost", dataPort) #welcomeConn[0] is IP of the FileServer
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
    " @summary
    """
    def CloseDataConnection(self):
        if(self.dataConnectionOpen == True):
            self.dataConnection.close()
            self.dataConnectionOpen = False

    """
    " @summary
    """
    def Quit(self):
        self.connected = False
        self.Run = False
        if(self.connected == True): self.controlConnection.close()

    """
    " @summary
    """
    def __del__(self):
        self.Quit()