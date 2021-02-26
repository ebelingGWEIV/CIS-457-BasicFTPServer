import Client
import FileServerManager
import _thread
import io
import time


def StartClient():
    myClient = Client.Client("127.0.0.1", 1602)
    myClient.createCommandConnection()
    return myClient


def StartServer():
    myServer = FileServerManager.FileServer("127.0.0.1", 1602)
    myServer.listenForCommands(2048)
    return myServer


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    _thread.start_new_thread(StartServer, ())
    _thread.start_new_thread(StartClient, ())
    go = 1
    while go == 1:
        go = int(input())
    _thread.exit()