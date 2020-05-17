import socket
import file_client
import login_conn
import pickle


dados = ['G', 'usuario']
msg = pickle.dumps(dados)
resultado = file_client.send(msg)
arquivos = pickle.loads(resultado)

print(type(dados))
print(type(msg))
print(type(resultado))
print(type(arquivos))
