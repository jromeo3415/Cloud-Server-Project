import socket
import time
import os
import pandas as pd
import threading
import csv

# Server-Side Code
class Server:
    # initialize a dictionary to store the server operations
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.stats = {
            'upload_speed': [],
            'download_speed': [],
            'file_transfer_time': [],
            'throughput': [],
        }
        # create a dataframe to hold performance metrics 
        # this dataframe's columns will correspond to the stats dictionary
        self.df = pd.DataFrame(columns=['upload_speed', 'download_speed', 'file_transfer_time', 'throughput'])

        self.write_lock = threading.Lock()
    
    # allow server to accept connections
    def start(self): 
        # create a new socket with the correct format
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"Server listening on {self.host}:{self.port}")
            # this is an infinite loop that allows the server to continue accepting connections
            while True:
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(conn,))
                client_thread.start()

    def handle_client(self, conn):
        start_time = time.time()
        
        # Receive file size
        file_size = int(conn.recv(1024).decode())
        print(f"File size to be transferred: {file_size} bytes")
        
        # Track the time for the file transfer
        transfer_start_time = time.time()
        bytes_received = 0
        # loop until file is completely recieved 
        while bytes_received < file_size:
            data = conn.recv(1024)
            if not data:
                break
            bytes_received += len(data)

        # time.time() will be the time the transfer stopped
        transfer_time = time.time() - transfer_start_time
        print(f"File transfer time: {transfer_time} seconds")
        
        # download speed (bytes per second) this is considered metric one alongside upload speed
        download_speed = bytes_received / transfer_time
        self.stats['download_speed'].append(download_speed)
        self.stats['file_transfer_time'].append(transfer_time)
        
        # Calculate throughput (data transferred per second)
        throughput = bytes_received / transfer_time
        self.stats['throughput'].append(throughput)

        # Add values to the DataFrame
        self.df = self.df.append({
            'download_speed': download_speed,
            'file_transfer_time': transfer_time,
            'throughput': throughput,
        }, ignore_index=True)

        # display results
        print(f"Download Speed: {download_speed} B/s, Transfer Time: {transfer_time} s, Throughput: {throughput} B/s")

        # Close the connection
        conn.close()

    def save_statistics(self):
        # Open the CSV file in write mode
        with open('server_files/network_statistics.csv', 'w', newline='') as csvfile:
            # Define the fieldnames (column names for the CSV file)
            fieldnames = ['upload_speed', 'download_speed', 'file_transfer_time', 'throughput']
        
            # DictWriter allows you to write the dictionaries into the csv file
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
            # Write the column names into the CSV file
            writer.writeheader()
        
            # Write the data (the rows) to the CSV file
            for index, row in self.df.iterrows():
                writer.writerow({
                    'upload_speed': row['upload_speed'],
                    'download_speed': row['download_speed'],
                    'file_transfer_time': row['file_transfer_time'],
                    'throughput': row['throughput'],
                })
    
        print("Statistics saved to network_statistics.csv")
        with open('output.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

# Client-Side Code
class Client:
    # initialize the host, port and file path
    def __init__(self, server_host='127.0.0.1', server_port=65432, file_path='test_file.txt'):
        self.server_host = server_host
        self.server_port = server_port
        self.file_path = file_path

    def send_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_host, self.server_port))

            # Get file size and send it 
            file_size = os.path.getsize(self.file_path)
            s.sendall(str(file_size).encode())

            # Start file transfer
            with open(self.file_path, 'rb') as f:
                start_time = time.time()
                bytes_sent = 0
                
                while (chunk := f.read(1024)):
                    s.sendall(chunk)
                    bytes_sent += len(chunk)
                transfer_time = time.time() - start_time

            # upload speed (bytes per second) this is metric one w/ download 
            upload_speed = bytes_sent / transfer_time
            print(f"File transfer complete. Time taken: {transfer_time} s, Upload speed: {upload_speed} B/s")

            # throughput aka rate (data sent per second) this is metric three
            throughput = bytes_sent / transfer_time
            print(f"Throughput: {throughput} B/s")

# Example of how to use the module
if __name__ == "__main__":
    # Start the server in a separate thread
    server = Server()
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    # Client sends a file
    client = Client(file_path='test_file.txt')
    client.send_file()

    # After the test, the server saves the stats to a CSV file
    server.save_statistics()


