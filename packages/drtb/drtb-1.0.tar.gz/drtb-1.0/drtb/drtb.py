#imports
import os
import sys
import platform
import socket
import requests
debug = 0
def title(type):
    if type == "source":
        print("""  _____  _____ _______ ____      _____ __  __ _____              _____  ____  _    _ _____   _____ ______ 
 |  __ \|  __ \__   __|  _ \    / ____|  \/  |  __ \            / ____|/ __ \| |  | |  __ \ / ____|  ____|
 | |  | | |__) | | |  | |_) |  | |    | \  / | |  | |  ______  | (___ | |  | | |  | | |__) | |    | |__   
 | |  | |  _  /  | |  |  _ <   | |    | |\/| | |  | | |______|  \___ \| |  | | |  | |  _  /| |    |  __|  
 | |__| | | \ \  | |  | |_) |  | |____| |  | | |__| |           ____) | |__| | |__| | | \ \| |____| |____ 
 |_____/|_|  \_\ |_|  |____/    \_____|_|  |_|_____/           |_____/ \____/ \____/|_|  \_\\\_____|______|
                                                                                                          
                                                                                                          """)
    elif type == "main":
        print("""  _____  _____ _______ ____      _____ __  __ _____ 
 |  __ \|  __ \__   __|  _ \    / ____|  \/  |  __ \ 
 | |  | | |__) | | |  | |_) |  | |    | \  / | |  | |   
 | |  | |  _  /  | |  |  _ <   | |    | |\/| | |  | | 
 | |__| | | \ \  | |  | |_) |  | |____| |  | | |__| | 
 |_____/|_|  \_\ |_|  |____/    \_____|_|  |_|_____/ 
                                                                                                          
                                                                                                          """)
def help():
    print("""List of all commands currently available
----------------------------------------
help - shows this list
cwd - prints where you are
cwd chdir - change where you are
mkdir - make a directory
rmdir - remove a directory (has to be empty)
listdir - list all directories where you are
rm - remove a file
sysinfo - shows system information
shutdown - shutdown computer
bios - enter bios
esc - terminate terminal
ip - shows your ip address
open-source - downloads the latest open source version of this software
update - downloads the latest version of this software
version - shows the current version of this software
pypackage - downloads the latest drtb package
debug - toggles debug mode
msg - send a message to a user on the same network
run - enter commands like in command prompt""")
def cwd():
    try:
        print(os.getcwd())
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def cwd_chdir():
    try:
        chdir = input("Set directory: ")
        os.chdir(chdir)
        print(os.getcwd())
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def mkdir():
    try:
        mkdir = input("Create directory: ")
        parent_dir = os.getcwd()
        dirpath = os.path.join(parent_dir, mkdir)
        os.mkdir(dirpath)
        print("Directory '% s' created" % mkdir)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def rmdir():
    try:
        rmdir = input("Remove directory: ")
        parent_dir = os.getcwd()
        dirpath = os.path.join(parent_dir, rmdir)
        os.rmdir(dirpath)
        print("Directory '% s' removed" % rmdir)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def listdir():
    try:
        dir_list = os.listdir(os.getcwd())
        print("Files and directories in '", os.getcwd(), "' :")
        print(dir_list)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def rm():
    try:
        rm = input("Remove file: ")
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir, rm)
        os.remove(path)
        print("File '% s' removed" % rm)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def sysinfo():
    try:
        print("username:",os.getlogin())
        print("machine:",platform.machine())
        print("version:",platform.version())
        print("platform:",platform.platform())
        print("system:",platform.system())
        print("processor:",platform.processor())
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def shutdown():
    try:
        verify = input("Are you sure you want to shutdown computer? (y, n): ")
        if verify.lower() == "y":
            print("shutting down")
            os.system("shutdown /s /t 1")
        elif verify.lower() == "yes":
            print("shutting down")
            os.system("shutdown /s /t 1")
        else:
            print("Cancelling...")
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def bios():
    try:
        verify = input("Entering BIOS requires a shutdown, continue? (y, n): ")
        if verify.lower() == "y":
            print("Entering BIOS")
            os.system("shutdown /r /fw")
        elif verify.lower() == "yes":
            print("Entering BIOS")
            os.system("shutdown /r /fw")
        else:
            print("Cancelling...")
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def esc():
    try:
        sys.exit("Terminal Terminated")
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def ip():
    try:
        IPAddr=socket.gethostbyname(socket.gethostname())
        print("Your computer IP Address is:",IPAddr)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def open_source():
    try:
        path = os.getcwd()
        url = 'https://raw.githubusercontent.com/DaRealTrueBlue/DRTB-CMD/main/drtb_cmd_source.py'
        r = requests.get(url, allow_redirects=True)
        open('drtb_cmd_source.py', 'wb').write(r.content)
        print("Downloaded latest open source version into:", path)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def update():
    try:
        path = os.getcwd()
        url = 'https://raw.githubusercontent.com/DaRealTrueBlue/DRTB-CMD/main/drtb_cmd.exe'
        r = requests.get(url, allow_redirects=True)
        open('drtb_cmd.exe', 'wb').write(r.content)
        print("Downloaded latest version into:", path)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def version(ver):
    try:
        print("Your DRTB CMD is running version:",ver)
        url = 'https://raw.githubusercontent.com/DaRealTrueBlue/DRTB-CMD/main/drtb_cmd_ver.txt'
        r = requests.get(url, allow_redirects=True)
        print("The latest version currently avaliable is:", r.content)
        if ver != r.content:
            verify = input("Would you like to update to the latest version? (y/n): ")
            if verify.lower() == "y" or verify.lower() == "yes":
                path = os.getcwd()
                url = 'https://raw.githubusercontent.com/DaRealTrueBlue/DRTB-CMD/main/drtb_cmd.exe'
                r = requests.get(url, allow_redirects=True)
                open('drtb_cmd.exe', 'wb').write(r.content)
                print("Updated latest version into:", path)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def pypackage():
    try:
        path = os.getcwd()
        url = 'https://raw.githubusercontent.com/DaRealTrueBlue/DRTB-CMD/main/drtb-1.0.tar.gz'
        r = requests.get(url, allow_redirects=True)
        open('drtb-1.0.tar.gz', 'wb').write(r.content)
        print("Downloaded latest python package into:", path)
        print("use 'pip install ./drtb-1.0.tar.gz' to install the package")
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def msg():
    try:
        user = input("Who would you like to send the message to?: ")
        message = input("What should the message say?: ")
        a = "msg " + user + " " + message
        os.system(str(a))
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def run():
    try:
        command = input("Enter command: ")
        os.system(command)
    except Exception as e:
        if debug == 1:
            print("Error:",e)
        else:
            print("There was an error")
def db():
    global debug
    if debug == 0:
        debug = 1
        print("Debug activated")
    else:
        debug = 0
        print("Debug deactivated")