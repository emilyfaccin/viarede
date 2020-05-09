'''Lidará com as solicitações de login vinda dos usuários
    Cliente envia os dados via socket (usuario, senha) e este servidor
    acessa o banco para a validação'''

import socket
import login_conn as lg

hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
PORT = 1236

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as login_server:
    login_server.bind((IP, PORT))
    login_server.listen()
    login_cliente, client_address = login_server.accept()

    with login_cliente:
        print('Connected by:', client_address)
        
        while True:
            dados = login_cliente.recv(1024).decode('utf-8').split(':')
            if not dados:
                break
            print(dados)
            status = lg.autenticar_usuario(lg.session, *dados)
            login_cliente.send(status.encode('utf-8'))
