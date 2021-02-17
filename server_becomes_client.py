import socket

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
        #start control server by throwing a thread at listenForCommands()


    def listenForCommands(self, buffer_size):
        while self.Run:
            controlCommand = self.connection_socket.recv(buffer_size).decode('ascii')
            print(controlCommand)
            #this should be run with a seperate thread. Here on after that thread will do everything
            self.parseCommand(controlCommand)

    def stopControlServer(self):
        self.Run = False

    def parseCommand(self, controlCmd):
        command = str(controlCmd).split(' ') #We're expecting a tuple?
        #this is where the thread should termiante itself

    #Perform one of the four commands
    def onCommand(self, command, dataIP, dataPort):
        if(command[0].toLower() == "connect"):
            pass
        elif(command[0].toLower() == "list"):
            pass
        elif(command[0].toLower() == "retr"):
            pass
        elif(command[0].toLower() == "stor"):
            pass
        elif(command[0].toLower() == "quit"):
            pass
        pass

    def __del__(self):
        self.controlSocket.close()

"""
server_ip = 'localhost'
server_port = 12000
buffer_size = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen()

connection_socket, addr = server_socket.accept()

new_port = int(connection_socket.recv(buffer_size).decode('ascii'))

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, new_port))

#Sends a success message
client_socket.send(str("successful connection").encode('ascii'))

# Close
client_socket.close()
server_socket.close()
"""