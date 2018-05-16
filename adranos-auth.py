import random
import time
import datetime
import sys
from pathlib import Path

configFile = "AdranosPi.cfg"
authFile = ""
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
length = 32
authKey = ""

def loadCfg(): # Load config that is use by both generator and server
        if Path(configFile).is_file():
                file = open(configFile, "r")
                for line in file:
                        if '#' not in line: # check if the line is a comment
                                global authFile # pull in the config array to edit
                                a = line.strip('\n').split('=')
                                if a[0] == "auth":
                                        authFile = a[1]
                file.close()
        else:
                print("[!] ERROR: Config file: '" + configFile + "' does not exist!")
                exit();

def printUsage():
        print("[#] Usage: ")
        print("[#] python adranos-auth.py [command] [value]")
        print("")
        print("[#] Commands: ")
        print("[+] add : requires no value. will add a key to your server and output it.")
        print("[-] remove : requires the key you wish to remove from the server")
        exit()

def generateKey():
        global authKey
        authKey = ""
        for i in range(length):
                j = random.randrange( len(chars) )
                authKey = authKey + chars[j]
        checkKey(authKey)

def checkKey(key):
        print("[#] Checking for duplicate key in file...")
        if Path(authFile).is_file():
                file = open(authFile, "r")
                for line in file:
                        a = line.strip('\n')
                        if a == key:
                                print("[!] Generated duplicate! Generating new key!")
                                generateKey()
                file.close()
        else:
                print("[!] AuthKey file does not exist! Creating one...")

def addKey():
        print("[+] Adding key to authFile...")
        file = open(authFile, "a")
        file.write(authKey + "\n")
        file.close()
        print("\n\n[*] Key: " + authKey)
        print("[#] Use this code to get request from the server!")

def remKey(key):
        if Path(authFile).is_file():
                file = open(authFile, "r")
                lines = file.readlines()
                file.close()
                count = 0
                file = open(authFile, "w")
                for line in lines:
                        if line != key + "\n":
                                file.write(line)
                        else:
                                count += 1
                if count == 0:
                        print("[!] Error: The key '" + key + "' was not found in the authFile!")
                else:
                        print("[+] The key '" + key + "' was removed from the authFile!")
        else:
                print("[!] Error: The authFile does not exist!")
loadCfg()

if len(sys.argv) < 2:
        printUsage()

if len(sys.argv) >= 2:
        if sys.argv[1] == "add":
                generateKey()
                addKey()
        elif sys.argv[1] == "remove" and len(sys.argv) > 2:
                remKey(sys.argv[2])
        else:
                printUsage()
