import Client
import _thread
import signal


def signal_handler(sig, frame):
    if(sig == signal.SIGINT):
        try:
            print("Please close using the 'quit' command")
        except:
            # This is needed because the thread that is created doesn't have a client
            pass


def help():
    print("--------------------------------------")
    print("connect <server IP> <port>")
    print("reg <user name> <speed>")
    print("quit")
    print("get <server> <port> <filename>")
    print("list")
    print("add <filename> <description>")
    print("--------------------------------------")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    msg = ""
    port = 1609
    server = "localhost"

    myClient = Client.Client(server)
    help()

    while myClient.serverRunning:
        msg = str(input("enter a command: "))
        command = msg.split()

        if command[0].lower() == "connect" and len(command) == 3:
            myClient.connectToServer(command[1], command[2])
        elif command[0].lower() == "reg" and len(command) == 3:
            myClient.Register(command[1], command[2])
        elif command[0].lower() == "quit":
            myClient.Quit()
            break
        elif command[0].lower() == "get" and len(command) == 4:
            myClient.Get(command[3], command[1], command[2])

        elif command[0].lower() == "list" and len(command) == 1:
            myClient.ListFiles()

        elif command[0].lower() == "add" and len(command) >= 3:
            print("description: ")
            print(command[2:])
            # name speed descriptor
            myClient.AddFile(command[1], command[2:])

        elif command[0].lower() == "search" and len(command) == 2:
            myClient.Search(command[1])

        elif command[0].lower() == "help" and len(command) == 1:
            help()

        else:
            print("Command not recognized")

    _thread.exit()
