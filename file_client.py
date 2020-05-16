import socket
#from main import SERVER_IP

SERVER_IP = '192.168.56.1' #
IP = SERVER_IP
PORT = 1238
HEADER = 10


def send(dados):
    file_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#
    file_cliente.connect((IP, PORT))
    file_cliente.sendall(dados)
    status = file_cliente.recv(100000000)
    file_cliente.close()
    return status