import socket
from main import SERVER_IP


IP = SERVER_IP
PORT = 1236

login_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(dados):
    login_cliente.connect((IP, PORT))
    login_cliente.sendall(dados.encode('utf-8'))
    status = login_cliente.recv(16).decode('utf-8')
    return status