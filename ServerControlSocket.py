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
    " @summary Handle all expected commands from the client (List, retr, stor, and quit)
    " @param message The full message received from the client as a string
    """
    def HandleMessage(self, message):
        try:
            command = str(message).split()
            if command[0].lower() == "list":
                self.List(command[1])
                pass
            elif command[0].lower() == "retr":
                self.Retreive(command[1], command[2])
                pass
            elif command[0].lower() == "stor":
                self.StoreFile(command[1], command[2])
                pass
            elif command[0].lower() == "quit":
                self.__del__()
            pass
        except:
            print("Client sent bad request that could not be responded to on the data port")


    """
    " @summary Handle the client command to return a directory list of the FileServer
    " @param dataPort The name of the port to send the list over
    """
    def List(self, dataPort):
        arr = os.listdir('./FileServer')
        message = ""
        for file in arr:
            message = message + file + '\n'
        self.SendData((message).encode('ascii'), dataPort)

    """
    " @summary Handle the client command to return a file
    " @param filename The name of the file to send the client
    " @param dataPort The name of the port to send the file over
    """
    def Retreive(self, filename, dataPort):
        try:
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
        except:
                print("Client sent bad request")
                self.SendBlankData(dataPort)

    """
    " @summary Handle the client command to store a file.
    " @param filename The name of the expected file
    " @param dataPort The port the file will be received over
    """
    def StoreFile(self, filename, dataPort):
        bytes = self.GetData(dataPort)
        print("got file")
        file = open('./FileServer/' + filename, 'wb')
        file.write(bytes)
        file.close()

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
        self.CloseDataConnection()

    """
    " @summary Safel delete using the Quit method
    """
    def __del__(self):
        self.Quit()