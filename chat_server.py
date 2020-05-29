import socket
import select
import login_conn as lg

# hostname vai receber o retorno da função da lib socket que traz o hostname
hostname = socket.gethostname()
# a constante IP vai receber o retorno da função da lib socket que traz um host por nome passando
# como parâmetro a variável hostname
IP = socket.gethostbyname(hostname)
# porta definida para o servidor de mensagens
PORT = 1234

# a variável server_socket é um objeto socket criado com a função socket.socket (ipv4 e tcp)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# opção utilizada par que o address do socket quando conectado possa ser reutilizado no futuro
# uma vez que nossa pretensão é criar o socket, enviar o dado, receber o retorno e fecha-lo,
# quantas vezes for necessário
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# função que conecta/liga o nosso socket à um IP e porta, especificados no início do programa
server_socket.bind((IP, PORT))

# socket começa a aguardar conexões
server_socket.listen()

# Lista de sockets para a função select.select()
sockets_list = [server_socket]

# Dicionario de clientes conectados - socket como chave, usuario como dado
clients = {}

print(f'Aguardando conexões em {IP}:{PORT}...')

# Lida com o recebimento de mensagens
def receive_message(client_socket):
    #try / except
    try:
        # recebe a mensagem do socket recebido como parametro > usuario:mensagem
        message = client_socket.recv(2048).decode('utf-8')
        # Se não recebemos dado nenhum, o socket cliente encerrou a conexão não bruscamente, por exemplo,
        # através da função socket.close() ou socket.shutdown(socket.SHUT_RDWR)
        if not len(message):
            # retorna falso
            return False
        # retorna o valor da mensagem
        return message
    except:
        # Se entrarmos nessa parte, o client encerrou a conexão bruscamente ou só perdeu a conexão
        return False
# loop infinito para lidar com conexões e mensagens novas enquanto o script rodar
while True:
    # select.select vai lidar com multiplas conexoes
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Itera sobre os sockets notificados
    for notified_socket in read_sockets:

        # Se o socket notificado é um socket_server - conexão nova, aceite
        if notified_socket == server_socket:

            # o resultado da função accept retorna o socket cliente conectado e o endereço
            client_socket, client_address = server_socket.accept()

            # o client deve enviar username de cara, essa parte recebe
            user = receive_message(client_socket)

            # Se falso, o cliente desconectou antes de enviar seu nome, volta para a 
            if user is False:
                continue
            
            # adiciona o socket aceito à lista select.select
            sockets_list.append(client_socket)

            # salva o nome do usuario no dicionario de clientes
            clients[client_socket] = user

            print('Nova conexão aceita de {}:{}, usuario: {}'.format(*client_address, user))
        # caso contrario, algum socket está mandando mensagem
        else:

            # receber mensagem
            message = receive_message(notified_socket)

            # se a mensagem é falsa, o cliente disconectou, remover o socket da lista de sockets
            # no select.select e no dicionario de usuarios
            if message is False:
                
                # Remove da lista usada pelo select.select
                sockets_list.remove(notified_socket)

                # Remove do dicionário de clientes
                del clients[notified_socket]

                continue

            # Pega o usuario pelo socket notificado, então nós saberemos quem mandou a mensagem
            user = clients[notified_socket]

            print(f'Mensagem recebida de {user}: {message}')

            # insere a mensagem enviada no banco
            lg.inserir_nova_mensagem(message, user)

            # Itera sobre os clientes conectados e faz o broadcast da mensagem
            for client_socket in clients:

                # Envia o usuario e mensagem
                client_socket.send(f'{user}:{message}'.encode('utf-8'))
                print('Broadcast', message, 'para', user,)

    # Lida com algumas exceções
    for notified_socket in exception_sockets:

        # Remove da lista usada por select.select
        sockets_list.remove(notified_socket)

        # Remove do dicionário de clientes
        del clients[notified_socket]