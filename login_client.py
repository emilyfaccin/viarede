import socket

IP = '192.168.1.6'
PORT = 1236

login_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
login_cliente.connect((IP, PORT))

def send(dados):
    login_cliente.send(dados.encode('utf-8'))
    status = login_cliente.recv(16).decode('utf-8')
    return status