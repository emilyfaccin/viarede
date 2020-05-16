'''Lidará com as solicitações de login vinda dos usuários
    Cliente envia os dados via socket (usuario, senha) e este servidor
    acessa o banco para a validação'''

import socket
import login_conn as lg

hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
PORT = 1236


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as login_server:
    login_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    login_server.bind((IP, PORT))
    login_server.listen()
    login_cliente, client_address = login_server.accept()

    with login_cliente:
        print('Conexão recebida de:', client_address)

        while True:
            dados = login_cliente.recv(1024).decode('utf-8').split(':')
            print(dados)
            if dados:
                status = lg.triagem(*dados)
                login_cliente.send(status.encode('utf-8'))
                login_cliente.close()
                login_cliente, client_address = login_server.accept()
            else:
                status = '401'
                login_cliente.send(status.encode('utf-8'))
