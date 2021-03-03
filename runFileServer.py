import FileServerManager
import signal
import sys

def signal_handler(sig, frame):
    print("Closing the server")
    myServer.closeControlServer()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler) # I thought this was necessary for clean closing of the server
    myServer = FileServerManager.FileServer("localhost", 1609)

