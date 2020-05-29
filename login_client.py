import socket
from main import SERVER_IP

# variável global importada do módulo main
IP = SERVER_IP
# porta definida para o servidor de login
PORT = 1236

# função para enviar dados via socket
def send(dados):
    # login_cliente é um objeto socket criado com socket.socket (ipv4 e tcp)
    login_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # conecta o socket no ip e porta definidos no inicio do script
    login_cliente.connect((IP, PORT))
    # envia a outra ponta do socket (server) os dados recebidos como parametro encodados para utf-8
    login_cliente.sendall(dados.encode('utf-8'))
    # a variavel status vai receber o que o server mandar
    status = login_cliente.recv(30).decode('utf-8')
    # fecha o socket
    login_cliente.close()
    # retorna o conteúdo da variável para quem chamar a função
    return status
