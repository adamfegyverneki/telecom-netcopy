import socket
import hashlib
import sys

def receive_file(server_ip, server_port, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        client_socket, _ = server_socket.accept()
        with open(file_path, "wb") as file:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file.write(data)
        client_socket.close()

def request_checksum(checksum_srv_ip, checksum_srv_port, file_id):
    message = f"KI|{file_id}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((checksum_srv_ip, checksum_srv_port))
        sock.sendall(message.encode())
        response = sock.recv(1024).decode()
        return response.split("|")

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":
    srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path = sys.argv[1:]
    file_id = int(file_id)

    receive_file(srv_ip, int(srv_port), file_path)
    checksum_len, received_checksum = request_checksum(chsum_srv_ip, int(chsum_srv_port), file_id)
    calculated_checksum = calculate_md5(file_path)

    if received_checksum and calculated_checksum == received_checksum:
        print("CSUM OK")
    else:
        print("CSUM CORRUPTED")