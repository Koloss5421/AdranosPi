import socket
import sys
import datetime
import time
from pathlib import Path
from thread import *
# [SETTINGS]
configFile = "AdranosPi.cfg"
logFile = "AdranosPi.log"

# [Config Array]
# The config array stores host, port, tempPath, authPath in that order!
config = {}
temps = [-1,-1]
authKeys = []

def log(mess, num): # log actions ( "Message", info level)
        st = datetime.datetime.fromtimestamp(time.time()).strftime('[%m-%d-%Y %H:%M:%S] ')
        file = open(logFile, "a")
        file.write(st)
        if num == 0: # Major issue
                file.write("[!] " + mess)
        if num == 1: # Minor issue or fix for major
                file.write("[*] " + mess)
        if num == 2: # standard log output
                file.write("[-] " + mess)
        if num == 3: # Comment output ( Starting info etc )
                file.write("[#] " + mess)
        file.write("\n")
        file.close()

def loadCfg(): # Load config that is use by both generator and server
        log("Attempting to load config file...", 3)
        if Path(configFile).is_file():
                file = open(configFile, "r")
                for line in file:
                        if '#' not in line: # check if the line is a comment
                                global config # pull in the config array to edit
                                a = line.strip('\n').split('=')
                                if a[0] == "port":
                                        config[ a[0] ] = int(a[1])
                                else:
                                        config[ a[0] ] = a[1]
                log("Config file loaded!", 3)
        else:
                log("[!] ERROR: Config file: '" + configFile + "' does not exist!", 0)
                exit();

def loadTemp():
        log("Attempting to load saved target temperature...", 3)
        if Path( config['temp'] ).is_file():
                file = open( config['temp'] , "r")
                tmp = file.read()
                temps[1] = int(tmp)
                file.close()
                log("Saved target temperature loaded!", 3)
        else:
                log("Could not load target temperature. Creating new file @ 69 Degrees", 1)
                file = open( config['temp'] , "w")
                file.write("69")
                temps[1] = 69
                file.close()
                log("Target temperature file created! Temp loaded.", 3)
def loadKeys():
        log("Attempting to load auth keys", 3)
        if Path(config['auth']).is_file():
                file = open( config['auth'] , "r")
                count = 0
                for line in file:
                        if '#' not in line:
                                global authKeys
                                authKeys.append( line )
                                count += 1
                log(str(count) + " Key(s) Loaded!", 1)
        else:
                log("No authKey file found! If one is added later, it can be loaded at request time", 0)

def saveTemp():
        log("Saving target temperature...", 3)
        file = open( config['temp'], "w")
        file.write(str(temps[1]))
        file.close()

def checkAuth(key):
        if Path(config['auth']).is_file():
                file = open( config['auth'], "r")
                for line in file:
                        if line == key + "\n":
                                return True
                return False
        else:
                log("AuthFile does not exist! Can't authorize requests!",0)

log("Starting AdranosPi Server", 3)
loadCfg()
loadTemp()
loadKeys()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
        s.bind((config['host'], config['port']))
except socket.errno:
        log("Binding Failed", 0)
        sys.exit()

s.listen(10)

conn, addr = s.accept()
log("Connection: " + addr[0] + ":" + str(addr[1]), 2)
while True:
        data = conn.recv(128)
        decData = data.decode()
        log("Request: " + decData.strip("\n"), 2)
        request = decData.strip("\n").split(',')
        if len(request) >= 2:
                loadKeys() # yes it kinda seems redundant but it is so keys can be added while running
                if checkAuth(request[0]):
                        if request[1] == "get":
                                conn.sendall(str(temps[0]) + "," + str(temps[1]))
                        if request[1] == "post" and len(request) > 2:
                                temps[1] = int( request[2] )
                                saveTemp()
                else:
                        log("Invalid auth key: '" + request[0] + "!", 0)
        if not data:
                break;

conn.close()
s.close()
