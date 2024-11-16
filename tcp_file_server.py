#tcp_file_server
import socket
import sys
import os

#creating socket
s = socket.socket()
host = '0.0.0.0' #does not need to be changed. allows server to listen on all addresses
port = 8080 #change value to whatever port you would like to use
os.makedirs("server_files", exist_ok=True) #directory holding uploaded files
BUFFER = 4096
def start_server():
    print("Server started")

    try: #error handling if host cant bind to port or ip
        s.bind((host, port))
        print("socket binded to %s" % (port))
        s.listen(5)

    except:
        print("Error: Could not bind host to port or address.")
        exit()

    while True:
        try:
            client, addr = s.accept()
            print('Got connection from ', addr)
        except:
            print("Error: Could not accept connection from client")

        #receiving command from client and storing
        command = client.recv(BUFFER).decode().strip()
        print(command)
        if command == "LIST": #client requests list of all files
            files = os.listdir("server_files")
            print(files)
            client.sendall(f"Files available:\n{chr(10).join(files)}\n".encode() if files != "[]" else "No files available.\n".encode())



#allows file to be run from command line
if __name__ == "__main__":
    start_server()