import socket

client_tcp = socket.socket()
host = '10.200.240.164'
port = 5001

client_tcp.connect((host, port))
