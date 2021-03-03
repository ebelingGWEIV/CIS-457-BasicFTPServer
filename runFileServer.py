import FileServerManager
import signal
import sys


def signal_handler(sig, frame):
    print("Closing the server")
    myServer.closeControlServer()


def getPortNumber():
    # If the user gave a port number, set it to that. Otherwise, use the default
    port = -1
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = int(1609)
    return port


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    welcomePort = int(getPortNumber())
    if 0 < welcomePort <= 65535:
        myServer = FileServerManager.FileServer("localhost", welcomePort)
    else:
        print("User gave an invalid port number")
