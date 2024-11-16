#tpc_file_client
import socket

s = socket.socket()
host = '10.200.240.164' #change to the ip address of the host machine
port = 5001 #change to desired port

def start_client():
    try:  #handling unavailable host
        s.connect((host, port))
    except:
        print("Could not establish connection to host. Please check host address and port number.")
        exit()
    while True: #infinite loop for commands for server
        command = input("Enter command (LIST, UPLOAD <filename>, DOWNLOAD <filename>, EXIT): ")
        s.sendall(command.encode())


#allows file to be ran from command line
if __name__ == "__main__":
    start_client()