import os


def getList():
    files = os.listdir("../FileServer")
    for f in files:
        print(f)
