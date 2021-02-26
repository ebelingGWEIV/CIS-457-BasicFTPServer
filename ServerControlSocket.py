import socket
import concurrent.futures
import os

class Controller(object):
    def __init__(self, connectionInfo):
        self.conn = connectionInfo[0]
        self.myClient = connectionInfo[1]

    def listenForCommands(self, buffer_size, max_workers=10):
        while self.Run:
            message = self.conn.recv(buffer_size).decode('ascii')
            if message.endswith('$'):
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    executor.submit(self.parseCommand, message[:len(message)-1])
                message = ''

    # Perform one of the four commands
    """
    @return True to 
    """
    def onCommand(self, command):
        if command[0].lower() == 'connect' and self.connected == False:
            self.connected = True
            server = str(command[1])
            port = int(command[2])
            self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.controlSocket.connect((server, port))
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
            self.__del__(self)
        pass

    def __del__(self):
        self.controlSocket.close()
        concurrent.futures.ThreadPoolExecutor.shutdown()