import socket
import errno
from threading import Thread
import select
from kivy.app import App

# socket global
client_socket = None

# função de thread que vai ouvir novas mensagens recebidas
def listen(incoming_message_callback, error_callback):
    # loop infinito, pra quando c
    while True:
        # armazena a mensagem recebida do server e decodifica de utf-8
        mensagem = client_socket.recv(1024).decode('utf-8')
        # guarda na variável app a referencia para o app rodando no momento
        app = App.get_running_app()
        # usa o screen manager pra pegar a tela de chat e usar a função adiciona_chat_historico
        # passando como parametro a mensagem recebida 
        app.screen_manager.get_screen(name='chat').adiciona_chat_historico(mensagem)


# Conecta ao servidor
def connect(ip, port, my_username, error_callback):
    # socket criado no escopo global
    global client_socket

    # a variável client_socket é um objeto socket criado com a função socket.socket (ipv4 e tcp)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Tenta
    try:
        # conecta o socket no ip e porta recebidos como parametro
        client_socket.connect((ip, port))
    except Exception as e:
        # Erro de conexão
        error_callback('Erro de conexão: {}'.format(str(e)))
        # retorna falso 
        return False

    # Prepara o nome do usuario (encoda utf-8)
    username = my_username.encode('utf-8')
    # Envia o usuario, primeiro dado aguardado pelo servidor
    client_socket.send(username)
    # inicia a thread que aguarda novas mensagens
    start_listening(print, print)
    return True

# Envia mensagem ao servidor
def send(message):
    # Faz o encode da mensagem para utf-8
    # usuario:mensagem
    message = message.encode('utf-8')
    # envia a mensagem passada como parametro
    client_socket.send(message)

# função que de fato cria a thread
def start_listening(incoming_message_callback, error_callback):
    # target > função listen definida acima, args > mensagens de erro
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()
