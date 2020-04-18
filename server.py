import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Cria um soquete
# socket.AF_INET - address family, IPv4, algumas outras possibilidades são AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Ajusta REUSEADDR (como socket option) para 1 no soquete
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, então o server informa ao sistema operacional que usará aquele IP e porta
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# Server agora "ouve" novas conexões
server_socket.listen()

# Lista de soquetes para select.select()
sockets_list = [server_socket]

# Lista de clientes conectados - soquete como chave, cabeçalho do usuário e nome como dado
clients = {}

print(f'Aguardando conexões em {IP}:{PORT}...')

# Lida com o recebimento de mensagens
def receive_message(client_socket):

    try:
        # Recebe nosso header contendo o tamanho da mensagem, seu tamanho é definido e constante
        message_header = client_socket.recv(HEADER_LENGTH)

        # Se não recebermos nenhuma msg, client fechou a conexão graciosamente, por exemplo usando socket.close:() ou socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Converte o header em um valor inteiro
        message_length = int(message_header.decode('utf-8').strip())

        # Retorna um objeto de header da msg e dados da msg
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Itera sobre os soquetes captados
    for notified_socket in read_sockets:

        # Se o soquete captado é o server - nova conexão, aceite-a
        if notified_socket == server_socket:

            # Aceita a nova conexão
            # Isso nos dá um novo soquete - client soquete, conectado a este client somente, é unico para aquele client
            # O outro objeto retornado é um set ip/porta
            client_socket, client_address = server_socket.accept()

            # Cliente deve mandar seu nome de início, receba-o
            user = receive_message(client_socket)

            # Se falso, client desconectou antes de mandar seu nome
            if user is False:
                continue

            # Adiciona o soquete aceito à lista select.select()
            sockets_list.append(client_socket)

            # Salvar também nome de usuario e cabeçalho do nome de usuario
            clients[client_socket] = user

            print('Nova conexão aceita de {}:{}, usuário: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Senão um soquete existente está mandando a msg
        else:

            # Recebe a msg
            message = receive_message(notified_socket)

            # Se falso, client desconectou, limpar
            if message is False:
                print('Conexão encerrada de: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove da lista de socket.socket()
                sockets_list.remove(notified_socket)

                # Remove da nossa lista de usuários
                del clients[notified_socket]

                continue

            # Pega o usuario por soquete captado, assim saberemos quem mandou a msg
            user = clients[notified_socket]

            print(f'Mensagem recebida de  {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Itera sobre os clients conectados e espalha a mensagem
            for client_socket in clients:

                # Mas não manda ele pra quem enviou a mensagem
                if client_socket != notified_socket:

                    # Manda o usuario e msg (ambos com seus headers)
                    # Nós vamos reusar aqui o header da msg enviada pelo emissor, e salvar o nome de usuario enviado pelo usuario quando se conectou
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Soquete execptions vai que né
    for notified_socket in exception_sockets:

        # Remove da lista para socket.socket()
        sockets_list.remove(notified_socket)

        # Remove da nossa lista de usuarios
        del clients[notified_socket]