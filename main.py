import client_becomes_sever
import server_becomes_client
import _thread
import time


def StartClient():
    myClient = client_becomes_sever.Client("127.0.0.1", 1609)
    myClient.createCommandConnection()
    return myClient


def StartServer():
    myServer = server_becomes_client.FileServer("127.0.0.1", 1609)
    myServer.listenForCommands(2048)
    return myServer


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    _thread.start_new_thread(StartServer, ())
    _thread.start_new_thread(StartClient, ())

    while 1:
        pass