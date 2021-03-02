import FileServerManager
import signal
import sys

def signal_handler(sig, frame):
    print("Closing the server")
    myServer.stopControlServer()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler) #allows for safe closing of the server
    myServer = FileServerManager.FileServer("localhost", 1609)
    myServer.ListenForConnections()

