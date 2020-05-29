'''Lidará com as solicitações de autenticação e criação de novo usuário e
    alteração de senha. Cliente envia os dados via socket (usuario, senha) 
    somente o servidor acessa o banco para a validação.'''

import socket
# importa o módulo de acesso ao BD
import login_conn as lg

# hostname vai receber o retorno da função da lib socket que traz o hostname
hostname = socket.gethostname()
# a constante IP vai receber o retorno da função da lib socket que traz um host por nome passando
# como parâmetro a variável hostname
IP = socket.gethostbyname(hostname)
# porta definida para o servidor de login
PORT = 1236

# com o socket criado através da função socket.socket (ipv4 e tcp) com o apelido de login_server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as login_server:
    # opção utilizada par que o address do socket quando conectado possa ser reutilizado no futuro
    # uma vez que nossa pretensão é criar o socket, enviar o dado, receber o retorno e fecha-lo,
    # quantas vezes for necessário
    login_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # função que conecta/liga o nosso socket à um IP e porta, especificados no início do programa
    login_server.bind((IP, PORT))
    # socket começa a aguardar conexões
    login_server.listen()
    # o resultado da função accept retorna o socket cliente conectado e o endereço
    login_cliente, client_address = login_server.accept()

    # com o socket login_cliente conectado
    with login_cliente:
        # printa no console, debuggin
        print('Conexão recebida de:', client_address)
        
        # loop infinito, para executar enquanto a conexão não for explicitamente encerrada
        while True:
            # a varável dados será o conteúdo recebido de login_cliente decodificado para utf-8. Isso retorna uma string
            # são enviadas mais de uma informação, separadas pelo caractere ":". A função split pega essa string como 
            # entrada e retorna uma lista com as partes separadas da string pelo delimitador
            # podem ser encaminhados para cá: cabeçalho, que indica a natureza da operação que queremos fazer,
            # nome do usuario e senha, uma vez que esse servidor pode ser usado para autenticação de usuario, criação e
            # alteração de senha
            dados = login_cliente.recv(1024).decode('utf-8').split(':')
            # se foi recebido algum dado
            if dados:
                # status vai receber o retorno da função triagem do módulo login_conn, tendo o desempacotamento
                # da lista dados como parâmetro
                status = lg.triagem(*dados)
                # envia ao socket cliente o retorno recebido encodado para utf-8
                login_cliente.send(status.encode('utf-8'))
                # fecha o socket
                login_cliente.close()
                # se prepara para receber uma nova conexão
                login_cliente, client_address = login_server.accept()
            # caso dados seja vazio
            else:
                # status recebe um código de erro
                status = '401'
                # envia ao socket cliente o status de erro
                login_cliente.send(status.encode('utf-8'))
