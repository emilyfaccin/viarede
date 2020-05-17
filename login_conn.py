import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
# from main import super_user

# encode = utf-8


# criando a engine - comunicação com o banco
# echo=True indica que será printado no console o comando real executado
engine = create_engine('sqlite:///viarede.db', echo=True, poolclass=NullPool)
Session = sessionmaker(bind=engine)

# Para usar a ORM precisamos de uma sessão
def get_session():
    session = Session()
    return session


Base = declarative_base()


# representacao da tabela usuario
class Usuario(Base):
    __tablename__ = 'usuarios'

    name = Column(String, primary_key=True)
    password = Column(String)
    mensagem = relationship('Mensagem', backref='usuarios')
    arquivo = relationship('Arquivo', backref='usuarios')

    def __repr__(self):
        return f'User {self.name}'


# representacao da tabela mensagem   
class Mensagem(Base):
    __tablename__ = 'mensagens'

    id = Column(Integer, primary_key=True)
    dado = Column(String)
    usuario = Column(String, ForeignKey('usuarios.name'), nullable=False)
    user = relationship('Usuario')

    def __repr__(self):
        return f'Mensagem {self.dado}'


class Arquivo(Base):
    __tablename__ = 'arquivos'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    binario = Column(LargeBinary)
    usuario = Column(String, ForeignKey('usuarios.name'), nullable=False)
    user = relationship('Usuario')

    def __repr__(self):
        return f'Arquivo {self.nome}'

# Base.metadata.create_all(engine)


def busca(nome):
    session = get_session()
    dados = session.query(Usuario).filter_by(name=nome).all()
    session.close()
    return dados


def mostra_todos_usuarios():
    session = get_session()
    lista_usuarios = session.query(Usuario).all()
    for usuario in lista_usuarios:
        print(usuario.__dict__)
    session.close()


def inserir_usuario(usuario, senha):
    session = get_session()
    sh = hashlib.sha1()
    sh.update(senha.encode('utf-8'))
    hash_value = sh.hexdigest()
    user = Usuario(name=usuario, password=hash_value)
    try:
        session.add(user)
        session.commit()
        return '200'
    except IntegrityError as e:
        # 409 conflict
        print(e)
        return '409'
    finally:
        session.close()
    
    
def alterar_usuario(nome, senha):
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.name == nome).one()
        sh = hashlib.sha1()
        sh.update(senha.encode('utf-8'))
        hash_value = sh.hexdigest()
        usuario.password = hash_value
        session.commit()
        return '200'
    except NoResultFound as e:
        print(e)
        return '404'
    finally:
        session.close()


def autenticar_usuario(usuario, senha):
    try:
        lista = busca(usuario)
        pessoa = lista[0]
        user = pessoa.name
        passwd = pessoa.password

        sh = hashlib.sha1()
        sh.update(senha.encode('utf-8'))
        hash_value = sh.hexdigest()

        if usuario == user and hash_value == passwd:
            print('200')
            return '200'
        else:
            print('401')
            return '401'

    except IndexError as e:
        print(e)
        print('404')
        return '404'


def triagem(id, usuario, senha):
    # A = autenticar
    # I = inserir
    # R = resetar senha

    if id == 'A':
        status = autenticar_usuario(usuario, senha)
    elif id == 'I':
        status = inserir_usuario(usuario, senha)
    elif id == 'R':
        status = alterar_usuario(usuario, senha)
    return status


def inserir_nova_mensagem(nova_mensagem, usuario):
    session = get_session()
    mensagem = Mensagem(dado=nova_mensagem,usuario=usuario)
    session.add(mensagem)
    session.commit()
    session.close()


def trazer_historico_mensagens():
    session = get_session()
    try:
        hist = session.query(Mensagem).all()
        historico = ''
        for mensagem in hist:
            historico += f'\n{mensagem.usuario}: {mensagem.dado}'
        return historico
    except:
        return '404'
    finally:
        session.close()


def triagem_arquivos(cabecalho, user, name=None, binary=None):
    # G = GET
    # P = POST
    # D = DOWNLOAD
    # H = HISTORY
    if cabecalho == 'G':
        status = get_arquivos()
    elif cabecalho == 'P':
        status = gravar_arquivo(nome=name, binario=binary, usuario=user)
    elif cabecalho == 'D':
        status = acessa_arquivo_por_nome(name)
    elif cabecalho == 'H':
        status = trazer_historico_mensagens()
    print(status)
    return status


def gravar_arquivo(nome, binario, usuario):
    session = get_session()
    arquivo = Arquivo(nome=nome, binario=binario, usuario=usuario)
    # try:
    session.add(arquivo)
    session.commit()
    return '200'
    # except:

    # finally:
        # session.close()


def get_arquivos():
    session = get_session()
    # lista com todos os arquivos salvos
    arquivos = session.query(Arquivo.nome).all()
    session.close()
    return arquivos


def acessa_arquivo_por_nome(nome):
    session = get_session()
    arquivo = session.query(Arquivo).filter_by(nome=nome).one()

    return arquivo

print(triagem_arquivos('H', 'user'))
# l = triagem_arquivos('G', 'usuario')
# print(list(map(type, l)))
# # print(type(l))
# def foo(n):
#     return n._asdict()
# print(list(map(foo, l)))

# print(get_arquivos())
#acessa_arquivo_por_nome('610 ADM - BOLETO 10 (04-2020).pdf')

#mostra_todos_usuarios()
#autenticar_usuario(session, 'usuario01', 'senha01')
#inserir_usuario('usuario02', 'senha02')
#inserir_usuario('usuario04', 'senha04')

# inserir_nova_mensagem('Segunda mensagem de teste no histórico', 'usuario02')
#trazer_historico_mensagens(session)
#print(alterar_usuario('user', 'user'))

# busca(session,'usuario03')
# usuarios = busca(session, 'usuario03')
# mostra_todos_usuarios(usuarios)
# session.query(User).filter(User.name == 'Emily Faccin').delete()