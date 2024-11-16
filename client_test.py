import socket

SERVER_HOST = '34.132.217.192'  # Replace with your VM's external IP
SERVER_PORT = 8080
BUFFER_SIZE = 4096

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(client_socket.recv(BUFFER_SIZE).decode())

    while True:
        command = input("Enter command (LIST, UPLOAD <filename>, DOWNLOAD <filename>, EXIT): ")
        client_socket.sendall(command.encode())
        response = client_socket.recv(BUFFER_SIZE).decode()
        print(response)
        if command.upper().startswith("UPLOAD"):
            filename = command.split(" ", 1)[1]
            with open(filename, "rb") as f:
                while (chunk := f.read(BUFFER_SIZE)):
                    client_socket.sendall(chunk)
        elif command.upper().startswith("DOWNLOAD"):
            filename = command.split(" ", 1)[1]
            with open(filename, "wb") as f:
                while True:
                    chunk = client_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)

if __name__ == "__main__":
    main()
