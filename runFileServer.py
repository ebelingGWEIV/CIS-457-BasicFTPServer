import ServerManager
import signal
import sys


def signal_handler(sig, frame):
    if(sig == signal.SIGINT):
        print("Closing the server")
        del myServer


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
        myServer = ServerManager.FileServer()
        myServer.Start("localhost", welcomePort)
    else:
        print("User gave an invalid port number")
