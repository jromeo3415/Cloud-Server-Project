#tcp_file_server
import socket
import sys
import os
import threading
from rsa import newkeys, decrypt

host = '0.0.0.0'  # does not need to be changed. allows server to listen on all addresses
port = 8080  # change value to whatever port you would like to use
os.makedirs("server_files", exist_ok=True)  # directory holding uploaded files
BUFFER = 4096

# Store user credentials
USERS = {
    "user": "pass"
}

# Generate public and private keys
public_key, private_key = newkeys(2048)


# function to handle user authentication
def authenticate_client(client):
    while True:
        try:
            # Send public key to client
            client.sendall(f"{public_key.n}:{public_key.e}".encode())

            # Receive encrypted credentials
            encrypted_creds = client.recv(BUFFER)
            decrypted_creds = decrypt(encrypted_creds, private_key).decode()
            username, password = decrypted_creds.split(':')

            # Verify credentials
            if username in USERS and USERS[username] == password:
                client.sendall("Authorization Success".encode())
                return True
            client.sendall("Authorization Failed".encode())

        except Exception as e:
            print(f"Authentication error: {e}")
            return False


# function to handle client requests after thread is made
def handle_client(client, addr):
    print(f"New connection from {addr}")
    
    # Check user credentials
    if not authenticate_client(client):
        print(f"Authentication failed for {addr}")
        client.close()
        return

    print(f"Handling authenticated client {client}")

    try:
        while True:
            # Receive the command from the client
            whole_command = client.recv(BUFFER).decode().strip()
            if not whole_command:
                break  # Client disconnected

            # Handle 'list' command
            if whole_command == "list":
                files = os.listdir("server_files")
                if files:
                    client.sendall(f"Files available:\n{chr(10).join(files)}".encode())
                else:
                    client.sendall("No files available.".encode())

            # Handle 'upload' command
            elif whole_command.startswith("upload"):
                command, file_name = whole_command.split(" ", 1)
                file_path = os.path.join("server_files", file_name)

                if os.path.exists(file_path):  # Check if file already exists
                    client.sendall("File already exists. Enter 'yes' to overwrite, 'no' to abort: ".encode())
                    overwrite = client.recv(BUFFER).decode().strip()  # Ask client to overwrite or not
                    if overwrite == "yes":
                        client.sendall("READY".encode())
                        with open(file_path, "wb") as folder:
                            while True:
                                data = client.recv(BUFFER)
                                if b"<EOF>" in data:  # End of file transmission character
                                    folder.write(data.replace(b"<EOF>", b""))  # taking eof out, closing file, then breaking loop
                                    folder.close()
                                    break
                                folder.write(data)
<<<<<<< HEAD

=======
>>>>>>> 63c96e5f67b9c98e808b07c90da788839c58ce55
                    else:
                        client.sendall("File not overwritten. Upload aborted.".encode())
                else:
                    # If file doesn't exist, upload it
                    client.sendall("READY".encode())
                    with open(file_path, "wb") as folder:
                        while True:
                            data = client.recv(BUFFER)
                            if b"<EOF>" in data:  # End of file transmission character
                                folder.write(data.replace(b"<EOF>", b""))  # taking eof out, closing file, then breaking loop
                                folder.close()
                                break
                            folder.write(data)

            # client requests to delete a file
            elif whole_command.startswith("delete "):
                delete(whole_command, client)
		    
            # client requests to download a file
            elif whole_command.startswith("download "):
                download(whole_command, client)

<<<<<<< HEAD
=======
            # client requests to download a file
            elif whole_command.startswith("download "):
                download(whole_command, client)

>>>>>>> 63c96e5f67b9c98e808b07c90da788839c58ce55
            # client requests to create/delete subfolder
            elif whole_command.startswith("subfolder "):
                subfolder(whole_command, client)

            # client requests to exit
            elif whole_command == "EXIT":
                break
<<<<<<< HEAD
		    
=======

>>>>>>> 63c96e5f67b9c98e808b07c90da788839c58ce55
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

    if os.path.exists(file_path):  # checking if file is already on server
        client.sendall("File already exists. Enter 'yes' to overwrite, and 'no' to abort: ".encode())
        overwrite = client.recv(BUFFER).decode().strip()  # clients request to overwrite or not

        if overwrite == "yes":  # client wishes to overwrite duplicate
            client.send("READY".encode())
            with open(file_path, "wb") as new_file:  # opening file and replacing contents
                while True:
                    data = client.recv(BUFFER)
                    if not data:  # stop receiving when data isnt sent
                        new_file.close()
                        break
                    new_file.write(data)

        elif overwrite == "no":  # client does not want to overwrite
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


# function to delete files
def delete(whole_command, client):
    command, file_name = whole_command.split(" ", 1)
    file_path = os.path.join("server_files", file_name)

    if not os.path.exists(file_path):
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
    command, file_name = whole_command.split(" ", 1)
    file_path = os.path.join("server_files", file_name)

<<<<<<< HEAD
    if not (os.path.exists(file_path)):
        client.sendall("Error: File does not exist".encode())
        return
    try:
        with open(file_path, "rb") as file: # open file
            client.sendall("READY".encode())
            while chunk := file.read(BUFFER): # send files in chunks
                client.send(chunk)
            client.send(b"<EOF>") # end of transfer
    except Exception as e:
        client.sendall("Error: " + str(e).encode())


# function to create or delete subfolders
def subfolder(whole_command, client):
    try:
        command, action, file_name = whole_command.split(" ", 2)
        file_path = os.path.join("server_files", file_name)

        # client create subfolder
        if action == "create":
            os.makedirs(file_path, exist_ok=True)
            client.sendall(f"Successfully created folder".encode())

        # client delete subfolder
        elif action == "delete":
            if os.path.exists(file_path): # check if directory exists
                if os.path.isdir(file_path): # check if path is directory
                    if not os.listdir(file_path):  # check if directory is empty
                        os.rmdir(file_path)
                        client.sendall(f"Successfully deleted folder".encode())
                    else:
                        client.sendall("Error: Folder is not empty".encode())
                else:
                    client.sendall("Error: Path is not a folder".encode())
            else:
                client.sendall("Error: Folder does not exist".encode())
        else:
            client.sendall("Error: Invalid subfolder action".encode())
=======
    if not os.path.exists(file_path):
        client.sendall("Error: File does not exist".encode())
        return
    try:
        with open(file_path, "rb") as file:  # open file
            client.sendall("READY".encode())
            while chunk := file.read(BUFFER):  # send files in chunks
                client.send(chunk)
            client.send(b"<EOF>")  # end of transfer
>>>>>>> 63c96e5f67b9c98e808b07c90da788839c58ce55
    except Exception as e:
        client.sendall("Error: " + str(e).encode())


# function to create or delete subfolders
def subfolder(whole_command, client):
    try:
        command, action, file_name = whole_command.split(" ", 2)
        file_path = os.path.join("server_files", file_name)

        # client create subfolder
        if action == "create":
            os.makedirs(file_path, exist_ok=True)
            client.sendall(f"Successfully created folder".encode())

        # client delete subfolder
        elif action == "delete":
            if os.path.exists(file_path):  # check if directory exists
                if os.path.isdir(file_path):  # check if path is directory
                    if not os.listdir(file_path):  # check if directory is empty
                        os.rmdir(file_path)
                        client.sendall(f"Successfully deleted folder".encode())
                    else:
                        client.sendall("Error: Folder is not empty".encode())
                else:
                    client.sendall("Error: Path is not a folder".encode())
            else:
                client.sendall("Error: Folder does not exist".encode())
        else:
            client.sendall("Error: Invalid subfolder action".encode())
    except Exception as e:
        client.sendall("Error: " + str(e).encode())


# starts server and initiates client thread
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


# allows file to be run from command line
if __name__ == "__main__":
    start_server()
