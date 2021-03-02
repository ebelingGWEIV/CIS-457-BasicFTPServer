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
        self.controlCon = connectionInfo[0]
        # myClient = connectionInfo[1]
        self.ip = connectionInfo[1][0]
        self.myPort = connectionInfo[1][1]
        self.Run = True
        self.dataConnectionOpen = False
        self.dataSeverOpen = False

    """
    " @summary
    """
    def StartControlServer(self):
        while(self.Run == True):
            try:
                message = self.controlCon.recv(Controller.buffer_size).decode('ascii')  # we assume that
                self.HandleMessage(message)
            except ConnectionResetError as ex:
                print("Server on port " + str(self.myPort) + " is closing")
                self.Quit()

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
            self.Quit()
        pass


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
        dataSocket.connect((self.ip, int(dataPort)))
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
            self.dataSocket.close()

    """
    " @summary
    """
    def Quit(self):
        self.Run = False
        self.CloseDataConnection()

    """
    " @summary
    """
    def __del__(self):
        self.Quit()