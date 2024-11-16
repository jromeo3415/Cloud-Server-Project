import os
import socket
import threading

SERVER_HOST = '0.0.0.0'  # Allows the server to listen on all available network interfaces
SERVER_PORT = 8080       # Port number for the server
BUFFER_SIZE = 4096       # Size of each data chunk
SHARED_DIR = "shared_files"  # Directory to store shared files

# Ensure the shared directory exists
os.makedirs(SHARED_DIR, exist_ok=True)

def handle_client(client_socket, client_address):
    print(f"[+] New connection from {client_address}")
    client_socket.sendall("Commands:\nLIST - List files\nUPLOAD <filename> - Upload file\nDOWNLOAD <filename> - Download file\nEXIT - Close connection\n".encode())

    while True:
        command = client_socket.recv(BUFFER_SIZE).decode().strip()
        if command.upper() == "LIST":
            files = os.listdir(SHARED_DIR)
            client_socket.sendall(f"Files available:\n{chr(10).join(files)}\n".encode() if files else "No files available.\n".encode())
        elif command.upper().startswith("UPLOAD"):
            filename = command.split(" ", 1)[1]
            client_socket.sendall("Ready to receive the file\n".encode())
            filepath = os.path.join(SHARED_DIR, filename)
            with open(filepath, "wb") as f:
                while (chunk := client_socket.recv(BUFFER_SIZE)):
                    f.write(chunk)
            client_socket.sendall(f"File '{filename}' uploaded.\n".encode())
        elif command.upper().startswith("DOWNLOAD"):
            filename = command.split(" ", 1)[1]
            filepath = os.path.join(SHARED_DIR, filename)
            if os.path.isfile(filepath):
                client_socket.sendall("Ready to send the file\n".encode())
                with open(filepath, "rb") as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        client_socket.sendall(chunk)
                client_socket.sendall(f"File '{filename}' downloaded.\n".encode())
            else:
                client_socket.sendall(f"File '{filename}' not found.\n".encode())
        elif command.upper() == "EXIT":
            client_socket.sendall("Connection closed.\n".encode())
            break
        else:
            client_socket.sendall("Unknown command.\n".encode())
    client_socket.close()
    print(f"[-] Connection closed from {client_address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Server started, listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
        print(f"[+] Started thread for {client_address}")

if __name__ == "__main__":
    start_server()
