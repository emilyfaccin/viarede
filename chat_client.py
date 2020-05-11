import socket
import errno
from threading import Thread
import select
from kivy.app import App

client_socket = None

def listen(incoming_message_callback, error_callback):
    while True:
        mensagem = client_socket.recv(1024).decode('utf-8')
        print(mensagem)
        app = App.get_running_app()
        app.screen_manager.get_screen(name='chat').adiciona_chat_historico(mensagem)


# Connects to the server
def connect(ip, port, my_username, error_callback):

    global client_socket

    # Create a socket
    # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
    # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to a given ip and port
        client_socket.connect((ip, port))
    except Exception as e:
        # Connection error
        error_callback('Connection error: {}'.format(str(e)))
        return False

    # Prepare username and header and send them
    # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
    username = my_username.encode('utf-8')
    client_socket.send(username)
    start_listening(print, print)

    return True

# Sends a message to the server
def send(message):
    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
    # usuario:mensagem
    message = message.encode('utf-8')
    client_socket.send(message)

# Starts listening function in a thread
# incoming_message_callback - callback to be called when new message arrives
# error_callback - callback to be called on error
def start_listening(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()

# Listens for incomming messages
# def listen(incoming_message_callback, error_callback):
#     while True:

#         try:
#             # Now we want to loop over received messages (there might be more than one) and print them
#             while True:
                
#                 # Receive and decode username
#                 dados = client_socket.recv(6000).decode('utf-8').split(':')
#                 username = dados[0]
#                 message = dados[1]

#                 # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
#                 if not len(message):
#                     error_callback('Connection closed by the server')


#                 # Print message
#                 incoming_message_callback(username, message)

#         except Exception as e:
#             # Any other exception - something happened, exit
#             error_callback('Reading error: {}'.format(str(e)))