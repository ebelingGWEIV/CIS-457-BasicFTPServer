class FileRefs(object):
    def __init__(self):
        self.files = []

    def search(self, keyword):
        hostList = []
        for entry in self.files:  # Could be parellized, but there won't be a noticeable difference due to the number of entries used for demonstration
            if entry[0].__contains__(keyword):
                hostList.append(entry[1])  # Add the host info
        return hostList

    def add(self, descript, fileTup):
        newTup = (descript, HostInfo(fileTup[0], fileTup[1], fileTup[2], fileTup[3]))
        self.files.append(newTup)

    def remove(self, files):
        for entry in self.files:
            if list(files).__contains__(entry[1]):
                print("removing " + entry[1].FileName)
                self.files.remove(entry)

    def list(self):
        fileList = []
        if len(self.files) == 0:
            return fileList

        for entry in self.files:
            host = entry[1]
            # print("host info " + host.FileName)
            fileList.append((host.FileName, host.Speed, host.HostName, host.PortNum))
        return fileList

class HostInfo:
    def __init__(self, file, host, port, speed):
        self.FileName = file
        self.HostName = host
        self.PortNum = port
        self.Speed = speed
