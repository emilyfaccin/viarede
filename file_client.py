import socket
from main import SERVER_IP

# variável global importada do módulo main
IP = SERVER_IP
# porta definida para o servidor de arquivos
PORT = 1238

# buffer aqui tem que ser monstro

# função para enviar dados via socket
def send(dados):
    # file_cliente é um objeto socket criado com socket.socket (ipv4 e tcp)
    file_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # conecta o socket no ip e porta definidos no inicio do script
    file_cliente.connect((IP, PORT))
    # envia a outra ponta do socket (server) os dados recebidos como parametro.
    # aqui não precisa de encode porque o pickle já serializou os dados
    file_cliente.sendall(dados)
    # a variavel status vai receber o que o server mandar
    status = file_cliente.recv(100000000)
    # fecha o socket
    file_cliente.close()
    # retorna o conteúdo da variável para quem chamar a função
    return status