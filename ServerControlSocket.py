import socket
import FileRefList

class Controller():
    buffer_size = 4096
    FileRefs = FileRefList.FileRefs()  # The list of all files and their hosts declared as a static class property
    Users = {} # Username, (host, speed)
    """
    " @summary
    " @param
    """
    def __init__(self, connectionInfo, timeout = 50.0, myIp = "localhost"):
        self.controlCon = connectionInfo[0]
        self.ip = connectionInfo[1][0]
        self.myPort = connectionInfo[1][1]
        self.myIP = myIp
        self.timeout = timeout
        self.Run = True
        self.registered = False

    """
    " @summary Receive messages from the client and send them to the message handler on a separate thread.
    """
    def RunControlServer(self):
        while(self.Run == True):
            try:
                message = self.controlCon.recv(Controller.buffer_size).decode('ascii')  # we assume that
                self.HandleMessage(message)
                self.Run = False
                self.__del__()
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
            print(f'received: {command} from {self.ip}')
            if command[0].lower() == "get":
                self.GetRequest(command[1])
                pass
            elif command[0].lower() == "post":
                print("not required")
                pass
            else:
                print("Command not supported")
                pass
        except ConnectionRefusedError as e:
            print("Connection over data port was refused. Cannot communicate, closing connection")
            self.Quit()
        except Exception as e:
            print(e)

    """
    " Build and send the response to a get request
    " @param path The path to a file
    """
    def GetRequest(self, path):
        try:
            fin = open('WebDir' + path)
            content = fin.read()
            fin.close()
            message = 'HTTP/1.0 200 OK\n\n'+ content
            self.SendData(message.encode('ascii'))
        except FileNotFoundError as ex:
            print("Client requested " + path + " but it was not found") # This is a good place to use the cookie
            self.Send404()
        pass

    def Send404(self):
        content = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'.encode('ascii')
        self.SendData(content)

    """
    " @summary Send data to the client
    " @param message The pre-constructed 'message' to send
    " @param dataPort The port to send data over
    """
    def SendData(self, message):
        self.controlCon.sendall(message)
        self.controlCon.close() # Needs to be closed for the client to know the message is complete

    """
    " @summary Sends an EOF message
    " @param dataPort The port to send data over
    """
    def SendBlankData(self):
        data = bytes(''.encode('ascii'))
        self.SendData(data)

    """
    " @summary Reset flags and close connection to the client.
    " @note The socket is closed in the FileServerManager
    """
    def Quit(self):
        self.Run = False
        self.dataConnectionOpen = False
        self.dataSeverOpen = False
        self.registered = False
        self.controlCon.close()


    """
    " @summary Safely delete using the Quit method
    """
    def __del__(self):
        self.Quit()