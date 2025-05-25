import socket

# === Создание UDP-сокета ===
def get_socket(host = "0.0.0.0", port=None, bind=False, timeout=0.01):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind:
        sock.bind((host, port))  
        sock.settimeout(timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock