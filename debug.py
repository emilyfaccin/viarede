import socket
import file_client
import login_conn
import pickle


usuario = 'usuario'
dados = ['H', usuario]
msg = pickle.dumps(dados)
resultado = file_client.send(msg)
status = pickle.loads(resultado)

print(dados)
print(type(dados))
print(msg)
print(type(msg))
print(resultado)
print(type(resultado))
print(status)
print(type(status))
