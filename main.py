import Client
import FileServerManager
import _thread


# Press the green button in the gutter to run the script.
#todo Add timeouts of 10ms to every socket
if __name__ == '__main__':
    msg = ""
    port = 1609
    server = "localhost"

    # _thread.start_new_thread(FileServerManager.FileServer, (server, port, )) #uncomment to run the server as part of the program

    myClient = Client.Client(server)

    while True:
        msg = str(input("enter a command"))
        command = msg.split()
        if command[0].lower() == "connect":
            myClient.connectToServer(command[1], command[2])
        elif command[0].lower() == "quit":
            myClient.Quit()
            break
        elif command[0].lower() == "retr":
            myClient.RetreiveFile(command[1])
        elif command[0].lower() == "stor":
            myClient.StoreFile(command[1])
        elif command[0].lower() == "list":
            myClient.ListFiles()

    _thread.exit()
