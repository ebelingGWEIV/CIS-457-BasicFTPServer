import Client
import ServerManager
import _thread


def help():
    print("--------------------------------------")
    print("connect <server IP> <port>")
    print("quit")
    print("get <server> <port> <filename>")
    print("list")
    print("add <filename> <speed> <description>")
    print("--------------------------------------")


if __name__ == '__main__':
    msg = ""
    port = 1609
    server = "localhost"

    # _thread.start_new_thread(FileServerManager.FileServer, (server, port, )) #uncomment to run the server as part of the program

    myClient = Client.Client(server)
    help()

    while True:
        msg = str(input("enter a command: "))
        command = msg.split()
        if command[0].lower() == "connect" and len(command) == 3:
            myClient.connectToServer(command[1], command[2])
        elif command[0].lower() == "quit":
            myClient.Quit()
            break
        elif command[0].lower() == "get" and len(command) == 4:
            myClient.Get(command[3], command[1], command[2])
        elif command[0].lower() == "list" and len(command) == 1:
            myClient.ListFiles()
        elif command[0].lower() == "add" and len(command) >= 4:
            print("description: ")
            print(command[3:])
            # name speed descriptor
            myClient.AddFile(command[1], command[2], command[3:])
        elif command[0].lower() == "search" and len(command) == 2:
            myClient.Search(command[1])
        elif command[0].lower() == "help" and len(command) == 1:
            help()
        else:
            print("Command not recognized")

    _thread.exit()
