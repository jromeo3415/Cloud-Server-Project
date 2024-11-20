#tpc_file_client
import socket
import os
import time

s = socket.socket()  # socket for client tcp file transfer
BUFFER = 4096 # packet size

# function to initialize connection to server
def connect(whole_command):
    try:  # handling too few or too many parts of command
        command, ip, port = whole_command.split(" ", 2)
    except ValueError:
        print("Error: Incorrect number of attributes")

    try:  # handling unavailable host
        port = int(port) #port is initially a string, converting to int
        s.connect((ip, port))
        print("Connected to %s on port: %s" % (ip, port))
    except:
        print("Error: Could not establish connection to host. "
              "Ensure server is running and host address and port are correct.")

# function to delete files from server
def delete(whole_command):
    try:
        command, file_path = whole_command.split(" ", 1)
        s.sendall(whole_command.encode())
        server_response = s.recv(BUFFER).decode()
        print(server_response)
    except ValueError: # handling file not on local device
        print("Error: File does not exist")
    except Exception as e: # handling when client tries to delete without connection to server
        print(f"Connect to server first!")


# function to upload file to server
def upload_file(whole_command):
    command, file_path = whole_command.split(" ", 1)

    # checking if file exists in local directory
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist locally.")
        return

    try:
        s.send(whole_command.encode())
    except OSError as e:
        print("Connect to server first!")
        return
    ack = s.recv(BUFFER).decode()

    # server is ready to write, send data
    if (ack == "READY"):
        try: # error handling for file not on local machine
            # start timer for performance evaluation
            start_time = time.time()
            with open(file_path, "rb") as local_file:
                total_sent = 0 # used to solve upload rate
                while chunk := (local_file.read(BUFFER)):  # loop to send packets until full file is sent
                    s.send(chunk)
                    total_sent += len(chunk)
                print("Upload complete. ")
                local_file.close()
                s.send(b"<EOF>")

             end_time = time.time()

            # calculates the file transfer time and upload rate in MB/s
            transfer_time = end_time - start_time
            upload_rate = total_sent / transfer_time / (1024 * 1024)

            print(f"File successfully sent to server. Transfer Time: {transfer_time:.2f} sec, Upload Rate: {upload_rate:.2f} MB/s")
            
        except FileNotFoundError:
            print(f"Error: file {file_path} not found on local device.")
        except Exception as e:
            print(f"Error: {e}")

    # file is already in server, requests to overwrite
    elif (ack.startswith("File already exists.")):
        overwrite_choice = input(ack)
        s.send(overwrite_choice.encode())
        overwrite_ack = s.recv(BUFFER).decode()


        # client chooses to overwrite
        if (overwrite_ack == "READY"):
            with open(file_path, "rb") as local_file:
                while chunk := (local_file.read(BUFFER)):
                    s.send(chunk)
                print("Upload complete. ")
                local_file.close()
                s.send(b"<EOF>")


        elif (overwrite_ack.startswith("File not overwritten. Upload aborted")):
            print(overwrite_ack)

        else:
            print("Error: Unexpected server ACK1")

    else:
        print("Error: Unexpected server ACK")


def start_client():
    while True: # infinite loop for commands for server
        try:
            whole_command = input("Enter command (connect <host ip> <port>, list, upload <filename>, download <filename>,\n"
                              " delete <filename>, subfolder {create|delete} path/directory, EXIT): ")
        except Exception as e:
            print(f"Error: {e}")

        # client requests to connect to server
        if whole_command.startswith("connect "):
            connect(whole_command)

        # client requests list of files
        elif whole_command == "list":
            s.sendall(whole_command.encode())
            file_list = s.recv(BUFFER).decode()
            print(file_list)

        # client requests to upload file
        elif whole_command.startswith("upload"):
            upload_file(whole_command)

        # client requests to delete file
        elif whole_command.startswith("delete"):
            delete(whole_command)

        elif whole_command.startswith("download"):
            s.sendall(whole_command.encode())

        else:
            print("Error: Command not recognized")


#allows file to be ran from command line
if __name__ == "__main__":
    start_client()
