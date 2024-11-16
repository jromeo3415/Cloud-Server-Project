#tpc_file_client
import socket

s = socket.socket()
host = '34.135.91.16' #change to the ip address of the host machine
port = 8080 #change to desired port

def start_client():
    try:  #handling unavailable host
        s.connect((host, port))
        print("Connected to %s on port: %s" %(host, port))
    except:
        print("Could not establish connection to host. Ensure server is running and host address and port are correct.")
        exit()
    while True: #infinite loop for commands for server
        command = input("Enter command (LIST, UPLOAD <filename>, DOWNLOAD <filename>, DELETE <filename>, EXIT): ")
        s.sendall(command.encode())
        response = s.recv(4096).decode()
        print(response)


#allows file to be ran from command line
if __name__ == "__main__":
    start_client()