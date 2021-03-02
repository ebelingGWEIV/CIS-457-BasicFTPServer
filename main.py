import Client
import FileServerManager
import _thread
import time

def StartServer(myServer):
    myServer.ListenForConnections()

# Press the green button in the gutter to run the script.
#todo Add timeouts of 10ms to every socket
if __name__ == '__main__':
    msg = ""
    port = 1609
    server = "localhost"

    myServer = FileServerManager.FileServer(server, port)
    myClient = Client.Client(server)

    _thread.start_new_thread(StartServer, (myServer, ))
    while msg != "quit all":
        msg = str(input("enter a command"))
        command = msg.split()
        if command[0].lower() == "connect":
            myClient.getCommandConnection(command[1], command[2])
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
