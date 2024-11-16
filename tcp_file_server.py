#tcp_file_server
import socket
import sys
import os

#creating socket
s = socket.socket()
host = '0.0.0.0' #does not need to be changed. allows server to listen on all addresses
port = 5001 #change value to whatever port you would like to use
os.makedirs("server_files", exist_ok=True) #directory holding uploaded files

def start_server():
    s.bind((host, port))
    print("socket binded to %s" % (port))

    s.listen(5)

    while True:
        c, addr = s.accept()
        print('Got connection from ', addr)

        c.send('Thanks'.encode())
        c.close()
        break

#allows file to be ran from command line
if __name__ == "__main__":
    start_server()