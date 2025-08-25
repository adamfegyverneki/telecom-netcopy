import socket
import threading
import time
import sys

class ChecksumServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.checksums = {}

    def handle_client(self, client_socket):
        data = client_socket.recv(1024).decode()
        if data.startswith("BE|"):
            self.store_checksum(data, client_socket)
        elif data.startswith("KI|"):
            self.retrieve_checksum(data, client_socket)
        client_socket.close()

    def store_checksum(self, data, client_socket):
        _, file_id, validity, checksum_len, checksum = data.split("|")
        expire_time = time.time() + int(validity)
        self.checksums[file_id] = (checksum, expire_time)
        client_socket.sendall(b"OK")

    def retrieve_checksum(self, data, client_socket):
        _, file_id = data.split("|")
        if file_id in self.checksums:
            checksum, expire_time = self.checksums[file_id]
            if time.time() < expire_time:
                response = f"{len(checksum)}|{checksum}"
            else:
                response = "0|"
                del self.checksums[file_id]
        else:
            response = "0|"
        client_socket.sendall(response.encode())

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, int(self.port)))
        server_socket.listen(5)
        print(f"Checksum Server listening on {self.ip}:{self.port}")
        while True:
            client_socket, _ = server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    ip, port = sys.argv[1], sys.argv[2]
    ChecksumServer(ip, port).run()