import socket
import hashlib
import sys

def send_file(server_ip, server_port, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        with open(file_path, "rb") as file:
            sock.sendall(file.read())

def upload_checksum(checksum_srv_ip, checksum_srv_port, file_id, checksum):
    message = f"BE|{file_id}|60|{len(checksum)}|{checksum}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((checksum_srv_ip, checksum_srv_port))
        sock.sendall(message.encode())
        response = sock.recv(1024).decode()
        return response == "OK"

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":
    srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path = sys.argv[1:]
    file_id = int(file_id)

    send_file(srv_ip, int(srv_port), file_path)
    checksum = calculate_md5(file_path)
    if upload_checksum(chsum_srv_ip, int(chsum_srv_port), file_id, checksum):
        print("Checksum uploaded successfully.")