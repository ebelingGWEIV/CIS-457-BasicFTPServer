class FileDict(object):
    def __init__(self):
        self.FileDict = {}

    def get(self, fileName):
        hostInfo = self.FileDict.get(fileName)
        return hostInfo

    def add(self, fileName, hostName, portNum):
        self.FileDict[fileName] = HostInfo(hostName, portNum)


class HostInfo:
    def __init__(self, host, port):
        self.HostName = host
        self.PortNum = port
