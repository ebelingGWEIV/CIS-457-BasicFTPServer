import Client
import FileServerManager
import _thread
import time

def StartClient(myClient, server, port):
    myClient.getCommandConnection(server, port)

def StartServer(myServer):
    myServer.ListenForConnections()

# Press the green button in the gutter to run the script.
#todo Add timeouts of 10ms to every socket
if __name__ == '__main__':
    msg = ""
    port = 1622
    server = "localhost"

    myServer = FileServerManager.FileServer()
    myClient = Client.Client(server)
    # while msg != "quit":
    #     msg = str(input("enter a command"))
    #     if(msg == "start server"):
    myServer.Create(server, 1611)
    _thread.start_new_thread(StartServer, (myServer, ))
    time.sleep(1)
        #     pass
        # elif(msg == "start only client"):
    myClient.Create(server, 1611)
    time.sleep(1)
    StartClient(myClient, server, port)
        # else:
        #     command = msg.split()
        #     if command[0].lower() == "connect":
            # myClient.createCommandConnection(command[1], command[2])
    # elif command[0].lower() == "quit":
    time.sleep(1)
    # myClient.RetreiveFile("test.txt")
    myClient.StoreFile("storeme.txt")
    # myClient.ListFiles()
    time.sleep(1)

    myClient.Quit()
    _thread.exit()