#tcp_file_server
import socket
import sys
import os

s = socket.socket()
host = '0.0.0.0' #does not need to be changed. allows server to listen on all addresses
port = 8080 #change value to whatever port you would like to use
os.makedirs("server_files", exist_ok=True) #directory holding uploaded files
BUFFER = 4096

# function to upload files
def upload(whole_command, client):
    command, file_name = whole_command.split(" ", 1)
    file_path = os.path.join("server_files", file_name)

    if (os.path.exists(file_path)):  # checking if file is already on server
        client.sendall("File already exists. Enter 'yes' to overwrite, and 'no' to abort: ".encode())
        overwrite = client.recv(BUFFER).decode().strip()  # clients request to overwrite or not

        if (overwrite == "yes"):  # client wishes to overwrite duplicate
            client.send("READY".encode())
            # file_path = os.path.join("server_files", file_name)
            with open(file_path, "wb") as new_file:  # opening file and replacing contents
                while True:
                    data = client.recv(BUFFER)
                    if not data:  # stop receiving when data isnt sent
                        new_file.close()
                        break
                    new_file.write(data)

        elif (overwrite == "no"):  # client does not want to overwrite
            client.sendall("File not overwritten. Upload aborted".encode())

        else:  # send error for non-fitting command
            client.sendall("Error: Command not recognized".encode())

    else:  # file doesnt already exist on server, write normally
        client.sendall("READY".encode())
        with open(file_path, "wb") as new_file:  # opening shared directory
            while True:
                data = client.recv(BUFFER)
                if not data:  # stop recieving when data isnt recieved
                    new_file.close()
                    break
                new_file.write(data)


#function to delete files
def delete(whole_command, client):
    command, file_name = whole_command.split(" ", 1)
    file_path = os.path.join("server_files", file_name)

    if not (os.path.exists(file_path)):
        client.sendall("Error: File does not exist".encode())
        return
    else:
        try:
            with open(file_path, "r+"):
                pass
        except IOError:
            client.sendall("Error: File is currently being processed".encode())
            return
    try:
        os.remove(file_path)
        client.sendall("Successfully removed".encode())
    except Exception as e:
        client.sendall("Error: " + str(e).encode())

def start_server():
    print("Server started")

    try: #error handling if host cant bind to port or ip
        s.bind((host, port))
        print("socket binded to %s" % (port))
        s.listen(5)

    except:
        print("Error: Could not bind host to port or address.")
        exit()

    try:
        client, addr = s.accept()
        print('Got connection from ', addr)
    except:
        print("Error: Could not accept connection from client")

    while True:
        #receiving command from client and storing
        whole_command = client.recv(BUFFER).decode().strip()

        #client requests list of files
        if whole_command == "list": #client requests list of all files
            files = os.listdir("server_files")
            print(files)
            client.sendall(f"Files available:\n{chr(10).join(files)}\n".encode() if files != "[]" else "No files available.\n".encode())

        #client requests to upload file
        elif whole_command.startswith("upload"):
            upload(whole_command, client)

        #client requests to delete file
        elif whole_command.startswith("delete"):
            delete(whole_command, client)

        else:
            print("Error: Command not recognized")
            break

#allows file to be run from command line
if __name__ == "__main__":
    start_server()