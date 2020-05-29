import socket
# módulo utilizado para serializar objetos em python
import pickle
# importa o módulo de acesso ao BD
import login_conn as lg

# hostname vai receber o retorno da função da lib socket que traz o hostname
hostname = socket.gethostname()
# a constante IP vai receber o retorno da função da lib socket que traz um host por nome passando
# como parâmetro a variável hostname
IP = socket.gethostbyname(hostname)
# porta definida para o servidor de arquivos
PORT = 1238

# buffer aqui tem que ser monstro

# com o socket criado através da função socket.socket (ipv4 e tcp) com o apelido de file_server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_server:
    # opção utilizada par que o address do socket quando conectado possa ser reutilizado no futuro
    # uma vez que nossa pretensão é criar o socket, enviar o dado, receber o retorno e fecha-lo,
    # quantas vezes for necessário
    file_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # função que conecta/liga o nosso socket à um IP e porta, especificados no início do programa
    file_server.bind((IP, PORT))
    # socket começa a aguardar conexões
    file_server.listen()
    # o resultado da função accept retorna o socket cliente conectado e o endereço
    file_cliente, client_address = file_server.accept()
    
    # com o socket file_cliente conectado
    with file_cliente:
        print('Conexão recebida de:', client_address)

        # loop infinito, para executar enquanto a conexão não for explicitamente encerrada
        while True:
            # a variável msg vai receber o que o socket cliente enviar
            msg = file_cliente.recv(100000000)
            # a variável dados será o conteúdo de msg desserializado. Como foi enviado o serial de uma
            # lista, após desserializar temos novamente uma lista contendo o cabeçalho, o usuario,
            # o binario e o nome do arquivo
            dados = pickle.loads(msg)
            # se foi recebido algum dado
            if dados:
                # status vai receber o retorno da função triagem_arquivos do módulo login_conn, tendo o
                # desempacotamento da lista dados como parâmetro
                status = lg.triagem_arquivos(*dados)
                # a função dumps serializa o objeto
                msg = pickle.dumps(status)
                # envia para o socket cliente o objeto serializado
                file_cliente.send(msg)
                # fecha o socket
                file_cliente.close()
                # se prepara para receber uma nova conexão
                file_cliente, client_address = file_server.accept()
            # caso dados seja vazio
            else:
                # 400: bad request
                status = '400'
                # envia ao socket cliente o status de erro
                file_cliente.send(status.encode('utf-8'))