#tcp_file_server
import socket
import sys
import os
import threading

host = '0.0.0.0' #does not need to be changed. allows server to listen on all addresses
port = 8080 #change value to whatever port you would like to use
os.makedirs("server_files", exist_ok=True) #directory holding uploaded files
BUFFER = 4096


# function to handle client requests after thread is made
def handle_client(client, addr):
    print(f"Handling client {client}")


    try:
        while True:
            # Receive the command from the client
            whole_command = client.recv(BUFFER).decode().strip()
            print(whole_command)
            if not whole_command:
                break  # Client disconnected

            # Handle 'list' command
            if whole_command == "list":
                files = os.listdir("server_files")
                if files:
                    client.sendall(f"Files available:\n{chr(10).join(files)}\n".encode())
                else:
                    client.sendall("No files available.\n".encode())

            # Handle 'upload' command
            elif whole_command.startswith("upload"):
                command, file_name = whole_command.split(" ", 1)
                file_path = os.path.join("server_files", file_name)
                print(file_path)

                if os.path.exists(file_path):  # Check if file already exists
                    client.sendall("File already exists. Enter 'yes' to overwrite, 'no' to abort: ".encode())
                    overwrite = client.recv(BUFFER).decode().strip()  # Ask client to overwrite or not
                    if overwrite == "yes":
                        client.sendall("READY".encode())
                        with open(file_path, "wb") as folder:
                            while True:
                                data = client.recv(BUFFER)
                                if not data:  # End of file transmission
                                    break
                                folder.write(data)
                        client.sendall(f"File {file_name} uploaded successfully.".encode())
                    else:
                        client.sendall("File not overwritten. Upload aborted.".encode())
                else:
                    # If file doesn't exist, upload it
                    client.sendall("READY".encode())
                    with open(file_path, "wb") as folder:
                        while True:
                            data = client.recv(BUFFER)
                            if not data:  # End of file transmission
                                break
                            folder.write(data)
                    client.sendall(f"File {file_name} uploaded successfully.".encode())

	        # client requests to delete a file
            elif(whole_command.startswith("delete ")):
                delete(whole_command, client)

            else:
                client.sendall("Unknown command.".encode())

    except Exception as e:
        print(f"Error handling client {client}: {e}")
    finally:
        print(f"Closing connection with {client}")
        client.close()  # Close the client connection


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


# function to download files to client
def download(whole_command, client):
    command, file = whole_command.split(" ", 1)


#starts server and initiates client thread
def start_server():
    print("Server started")

    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    print(f"Listening on {host}:{port}")

    while True:
        try:
            client, addr = s.accept()
            print(f"Got connection from {client}")

            client = threading.Thread(target=handle_client, args=(client, addr))
            client.daemon = True
            client.start()
        except Exception as e:
            print(f"Error: could not accept connection: {e}")


#allows file to be run from command line
if __name__ == "__main__":
    start_server()