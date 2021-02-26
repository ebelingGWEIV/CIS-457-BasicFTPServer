import socket
import concurrent.futures
import time
import os
import FileList


class FileServer(object):
    """
    @param server IP of the Command connection
    """
    def __init__(self, server, controlPort):
        self.Run = True
        self.serverIP = server
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.bind((server, controlPort))
        print("created server")
        self.controlSocket.listen()
        print("waiting for connection")
        self.connection_socket, addr = self.controlSocket.accept()


    def listenForCommands(self, buffer_size, max_workers=10):
        while self.Run:
            message = self.connection_socket.recv(buffer_size).decode('ascii')
            if message.endswith('$'):
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    executor.submit(self.parseCommand, message[:len(message)-1])
                message = ''

    def stopControlServer(self):
        self.Run = False

    def parseCommand(self, controlCmd):
        command = str(controlCmd).split(' ')
        self.onCommand(command)

        #this is where the thread should termiante itself

    #Perform one of the four commands
    def onCommand(self, command):
        if command[0].lower() == 'connect':
            time.sleep(2)
            print("got connected")
            pass
        elif command[0].lower() == "list":
            print("got list")
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                print(f)
            pass
        elif command[0].lower() == "retr":
            print("got retr")
            pass
        elif command[0].lower() == "stor":
            print("got stor")
            pass
        elif command[0].lower() == "quit":

            self.__del__()
            pass
        pass

    def __del__(self):
        self.controlSocket.close()
        concurrent.futures.ThreadPoolExecutor.shutdown()