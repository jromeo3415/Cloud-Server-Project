import socket

client_tcp = socket.socket()
host = '10.200.240.164'
port = 5001

try:
    client_tcp.connect((host, port))
except:
    print("Could not establish connection to host. Please check host address and port number.")
    exit()