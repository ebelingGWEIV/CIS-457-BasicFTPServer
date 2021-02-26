import Client
import FileServerManager
import _thread
import io
import time


def StartClient():
    myClient.createCommandConnection()


def StartServer():
    myServer.listenForCommands(2048)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    msg = ""
    port = 1602
    server = "127.0.0.1"
    while msg != "quit":
        msg = str(input("enter a command"))
        if(msg == "start server"):
            myServer = FileServerManager.FileServer("server", port)
            _thread.start_new_thread(StartServer, ())
            pass
        elif(msg == "start only client"):
            myClient = Client.Client("server", port)
            _thread.start_new_thread(StartClient, ())
        else:
            command = msg.split()
            if command[0].lower() == "connect":
                myClient.createCommandConnection(command[1], command[2])

_thread.exit()