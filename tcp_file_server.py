import socket
import sys

server_tcp = socket.socket()
host = '0.0.0.0'
port = 5001

server_tcp.bind((host, port))
print("socket binded to %s" %(port))

server_tcp.listen(5)

while True:
    c, addr = server_tcp.accept()
    print('Got connection from ', addr)

    c.send('Thanks'.encode())
    c.close()
    break