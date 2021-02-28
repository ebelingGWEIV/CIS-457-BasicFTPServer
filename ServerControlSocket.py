import socket
import concurrent.futures
import os
import time

class Controller():
    def __init__(self, connectionInfo):
        self.welcomeConn = connectionInfo[0]
        myClient = connectionInfo[1]
        self.connected = False
        self.Run = True
        self.StartControlServer()
        self.listenForCommands()

    def StartControlServer(self):
        while(self.connected == False):
            message = self.welcomeConn.recv(4096).decode('ascii')  # we assume that
            self.HandleMessage(message)

    def listenForCommands(self):
        while self.Run:
            message = self.controlConnection.recv(4096).decode('ascii') #we assume that
            self.HandleMessage(message)

    def HandleMessage(self, message, max_workers=10):
        if message.endswith('$'):
            print("server got " + message)
            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                executor.submit(self.onCommand, message[:len(message) - 1])
            message = ''

    """
    @return True to 
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
            print("got stor")
            pass
        elif command[0].lower() == "quit":
            self.Quit()
        pass

    def Connect(self, command):
        self.controlServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlServer.bind((command[1], int(command[2])))
        self.controlServer.listen()
        self.controlConnection, self.clientAddr = self.controlServer.accept()
        self.connected = True

    def List(self, dataPort):
        arr = os.listdir('./FileServer')
        message = ""
        for file in arr:
            message = message + file + '\n'
        self.SendData((message).encode('ascii'), dataPort)

    def Retreive(self, filename, dataPort):
        file = open('./FileServer/'+filename, 'rb')
        newChar = file.read(1)
        data = bytes(''.encode('ascii'))
        while newChar:
            data = data + newChar
            newChar = file.read(1)
            if not newChar:
                break
        self.SendData(data, dataPort)
        file.close()
        pass

    def SendData(self, message, dataPort):
        time.sleep(1) #to ensure connection happens
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.connect((self.clientAddr[0], int(dataPort)))
        dataSocket.send(message)
        dataSocket.close() #sends an EOF

    def Quit(self):
        self.connected = False
        self.Run = False
        if(self.connected == True): self.controlConnection.close()


    def __del__(self):
        self.Quit()
        # concurrent.futures.ThreadPoolExecutor.shutdown()