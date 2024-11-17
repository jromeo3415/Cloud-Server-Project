#tpc_file_client
import socket

s = socket.socket() #socket for client tcp file transfer
host = '35.225.209.17' #change to the ip address of the host machine
port = 8080 #change to desired port
BUFFER = 4096 #packet size


def start_client():
    try:  #handling unavailable host
        s.connect((host, port))
        print("Connected to %s on port: %s" %(host, port))
    except:
        print("Error: Could not establish connection to host. Ensure server is running and host address and port are correct.")
        exit()
    while True: #infinite loop for commands for server
        whole_command = input("Enter command (list, upload <filename>, download <filename>, delete <filename>, subfolder {create|delete} path/directory, EXIT): ")


        #client requests list of files
        if whole_command == "list":
            s.sendall(whole_command.encode())
            print(s.recv(BUFFER).decode())

        #client requests to upload file
        elif whole_command.startswith("upload"):
            command, file_path = whole_command.split(" ", 2)
            s.sendall(whole_command.encode())
            ack = s.recv(BUFFER)


            # server is ready to write, send data
            if(ack == "READY"):
                with open(file_path, "wb") as folder:
                    while chunk := (folder.read(BUFFER)):#loop to send packets until full file is sent
                        s.send(chunk)

            #file is already in server, requests to overwrite
            elif(ack.startswith("File")):
                overwrite_choice = input(ack)
                s.send(overwrite_choice.encode())
                overwrite_ack = s.recv(BUFFER)

                #client chooses to overwrite
                if(overwrite_ack == "READY"):
                    with open(file_path, "wb") as folder:
                        while chunk := (folder.read(BUFFER)):
                            s.send(chunk)

                else:
                    print("Error: Unexpected server ACK")

            else:
                print("Error: Unexpected server ACK")


        elif whole_command.startswith("download"):
            s.sendall(whole_command.encode())

        else:
            print("Error: Command not recognized")


#allows file to be ran from command line
if __name__ == "__main__":
    start_client()