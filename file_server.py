import socket
import pickle
import login_conn as lg

hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
PORT = 1238

# buffer aqui tem que ser monstro

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_server:
    file_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    file_server.bind((IP, PORT))
    file_server.listen()
    file_cliente, client_address = file_server.accept()

    with file_cliente:
        print('Conexão recebida de:', client_address)

        while True:
            msg = file_cliente.recv(100000000)
            dados = pickle.loads(msg)
            print(dados)
            if dados:
                status = lg.triagem_arquivos(*dados)
                print(type(status))
                # se o status for 200 a op feita foi gravar arquivo
                # if status == '200':
                msg = pickle.dumps(status)
                file_cliente.send(msg)
                print(type(msg))
                file_cliente.close()
                file_cliente, client_address = file_server.accept()
                # se o status for diferente de 200 a op feita foi buscar arquivos
                # else:
                #     file_cliente.send(status)
                #     file_cliente.close()
                #     file_cliente, client_address = file_server.accept()
            else:
                # 400: bad request
                status = '400'
                file_cliente.send(status.encode('utf-8'))