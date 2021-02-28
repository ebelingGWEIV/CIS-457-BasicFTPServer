import socket
import concurrent.futures
import os

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
            self.controlServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.controlServer.bind((command[1], int(command[2])))
            self.controlServer.listen()
            self.controlConnection, addr = self.controlServer.accept()
            self.connected = True
            pass
        elif command[0].lower() == "list":
            arr = os.listdir('./FileServer')
            for f in arr:
                print(f)
            pass
        elif command[0].lower() == "retr":
            print("got retr")
            pass
        elif command[0].lower() == "stor":
            print("got stor")
            pass
        elif command[0].lower() == "quit":
            self.Quit(self)
        pass

    def Quit(self):
        self.connected = False
        self.Run = False
        if(self.connected == True): self.controlConnection.close()


    def __del__(self):
        self.Quit()

        # concurrent.futures.ThreadPoolExecutor.shutdown()