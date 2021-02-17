import socket

class Client(object):
    """
    @param server IP of the Data connection
    """
    def __init__(self, server, port):
        self.controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controlSocket.connect((server, port))
        print("created client")


    def createCommandConnection(self):
        self.controlSocket.send(("Hello, I am the client").encode('ascii'))  # Sends port name

    def __del__(self):
        self.controlSocket.close()
"""
server_name = 'localhost'
server_port = 12000
new_port = 12002
buffer_size = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_name, server_port))
client_socket.send(str(new_port).encode('ascii')) # Sends port name

# Open the server socket and listen
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_name, new_port))
server_socket.listen()

# Accept the new connection
connection_socket, addr = server_socket.accept()

# Receive message and print
message = str(connection_socket.recv(buffer_size).decode('ascii'))
print("new message: " + message)

# Close sockets
client_socket.close()
server_socket.close()
"""