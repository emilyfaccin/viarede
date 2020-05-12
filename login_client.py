import socket
#from main import SERVER_IP

SERVER_IP = '192.168.56.1' #
IP = SERVER_IP
PORT = 1236

#login_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(dados):
    login_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#
    login_cliente.connect((IP, PORT))
    login_cliente.sendall(dados.encode('utf-8'))
    status = login_cliente.recv(30).decode('utf-8')
    login_cliente.close()
    return status
