#tcp_file_server
import socket
import sys
import os

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
        whole_command = client.recv(BUFFER).decode().strip()

        #client requests list of files
        if whole_command == "list": #client requests list of all files
            files = os.listdir("server_files")
            print(files)
            client.sendall(f"Files available:\n{chr(10).join(files)}\n".encode() if files != "[]" else "No files available.\n".encode())

        #client requests to upload file
        elif whole_command.startswith("upload"):
            command, file_name = whole_command.split(" ",2)

            if(os.path.exists(file_name)): #checking if file is already on server
                client.sendall("File already exists. Enter 'yes' to overwrite, and 'no' to abort.".encode())
                overwrite = client.recv(BUFFER).decode().strip() #clients request to overwrite or not

                if(overwrite == "yes"): #client wishes to overwrite duplicate
                    client.sendall("READY".encode())
                    file_path = os.path.join("server_files", file_name)
                    with open(file_path, "wb") as folder: #opening file and replacing contents
                        while True:
                            data = client.recv(BUFFER)
                            if not data:  # stop receiving when data isnt sent
                                break
                            folder.write(data)

                elif(overwrite == "no"): #client does not want to overwrite
                    client.sendall("File not overwritten. Upload aborted")
                    break

                else: #send error for non-fitting command
                    client.sendall("Error: Command not recognized")
                    break

            else: #file doesnt already exist on server, write normally
                file_path = os.path.join("server_files", file_name)
                client.sendall("READY".encode())
                with open(file_path, "wb") as folder: #opening shared directory
                    while True:
                        data = client.recv(BUFFER)
                        if not data: #stop recieving when data isnt recieved
                            break
                        folder.write(data)

#allows file to be run from command line
if __name__ == "__main__":
    start_server()