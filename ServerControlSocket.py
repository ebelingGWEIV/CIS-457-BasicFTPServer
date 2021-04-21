import socket
import FileRefList

class Controller():
    buffer_size = 4096
    FileRefs = FileRefList.FileRefs()  # The list of all files and their hosts declared as a static class property
    Users = {} # Username, (host, speed)
    """
    " @summary
    " @param
    """
    def __init__(self, connectionInfo, timeout = 50.0, myIp = "localhost"):
        self.controlCon = connectionInfo[0]
        self.ip = connectionInfo[1][0]
        self.myPort = connectionInfo[1][1]
        self.myIP = myIp
        self.timeout = timeout
        self.Run = True
        self.registered = False

    """
    " @summary Receive messages from the client and send them to the message handler on a separate thread.
    """
    def RunControlServer(self):
        while(self.Run == True):
            try:
                message = self.controlCon.recv(Controller.buffer_size).decode('ascii')  # we assume that
                self.HandleMessage(message)
                self.Run = False
                self.__del__()
            except ConnectionResetError as ex:
                print("Client closed forcibly. Server on port " + str(self.myPort) + " is closing")
                self.Quit()

    """
    " @summary Handle all expected commands from the client
    " @param message The full message received from the client as a string
    """
    def HandleMessage(self, message):
        try:
            command = str(message).split()
            if len(command) == 0: return
            print(f'received: {command} from {self.ip}')
            if command[0].lower() == "get":
                cookie = self.FindCookie(command)
                self.GetRequest(command[1], cookie)
                pass
            elif command[0].lower() == "post":
                print("not required")
                pass
            else:
                print("Command not supported")
                pass
        except ConnectionRefusedError as e:
            print("Connection over data port was refused. Cannot communicate, closing connection")
            self.Quit()
        except Exception as e:
            print(e)

    """
    " Build and send the response to a get request
    " @param path The path to a file
    """
    def GetRequest(self, path, cookie):
        count = 0
        if path == '/':
            path = '/home.html'
        elif path[1] == '%': #This is for responding to the CSS request
            path = path.split('\'')
            path = '/' + path[3] #the name of the css requested, hopefully
        try:
            fin = open('WebDir' + path)
            content = fin.read()
            fin.close()

            message = 'HTTP/1.0 200 OK/\n'

            isPageRequest = path[-5:] == '.html' # a bool that marks if the request was for the page or css
            Cookie, count = self.AccessCookieHeader(cookie, isPageRequest)

            if path == "/home.html":
                # This is so that other pages can be loaded without html being injected into the page.
                # A better solution would be to have a keyword that can be looked for in the html and then replaced.
                message = message + Cookie + '\n\n' + content + str(count) + "</p></body></html>"
            else:
                message = message + cookie + '\n\n' + content

            self.SendData(message.encode('ascii'))
        except FileNotFoundError as ex:
            print("Client requested " + path + " but it was not found") # This is a good place to use the cookie
            self.Send404()
        pass

    """
    " Reply to the client with a 404 code
    """
    def Send404(self):
        content = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'.encode('ascii')
        self.SendData(content)

    """
    " Only supports one cookie
    " @param requestArgs the split list of the message recieved from the client
    """
    def FindCookie(self, requestArgs):
        foundCookie = False
        for arg in requestArgs:
            myStr = str(arg)
            if(foundCookie == True):
                if(myStr == 'Cache-Control:'):  # If we find this, then the cookie we couldn't find the cookie we were looking for
                    foundCookie = False
                    return ''
                else:
                    cookieParts = myStr.split('=')
                    if(cookieParts[0] == 'access_count'): # We finally found the cookie
                        return myStr
            elif(myStr == 'Cookie:'):
                foundCookie = True
        return ''

    """
    " Create a cookie for counting the number of times a user has accessed/loaded a page from this server
    """
    def AccessCookieHeader(self, cookie, incrementCount):
        if len(cookie) == 0:
            newCookie = 'Set-Cookie: access_count=0'
            count = 0
        else:
            newCookie = cookie.split('=')
            count = (int(newCookie[1][:-1]))
            if incrementCount: count = count + 1
            newCookie = 'Set-Cookie: access_count=' + str(count)
        return (newCookie + ';Date: Tue, 20 Apr 2021 13:37:17 GMT; Expires=Tue, 4 May 2021 02:00:00 GMT/', count)

    """
    " @summary Send data to the client
    " @param message The pre-constructed 'messagae' to send
    " @param dataPort The port to send data over
    """
    def SendData(self, message):
        self.controlCon.sendall(message)
        self.controlCon.close() # Needs to be closed for the client to know the message is complete

    """
    " @summary Sends an EOF message
    " @param dataPort The port to send data over
    """
    def SendBlankData(self):
        data = bytes(''.encode('ascii'))
        self.SendData(data)

    """
    " @summary Reset flags and close connection to the client.
    " @note The socket is closed in the FileServerManager
    """
    def Quit(self):
        self.Run = False
        self.dataConnectionOpen = False
        self.dataSeverOpen = False
        self.registered = False
        self.controlCon.close()


    """
    " @summary Safely delete using the Quit method
    """
    def __del__(self):
        self.Quit()