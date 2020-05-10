import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import hashlib

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
    binario = Column(LargeBinary)
    usuario = Column(String, ForeignKey('usuarios.name'), nullable=False)
    user = relationship('Usuario')

    def __repr__(self):
        return f'Mensagem {self.id}'

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
    session.add(user)
    session.commit()
    session.close()


# def altera_usuario(User, nome, senha):
#     update = User.update().\
#                 where(User.name == nome).\
#                 values(name=nome, password=senha)


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



def inserir_nova_mensagem(nova_mensagem, usuario):
    session = get_session()
    mensagem = Mensagem(dado=nova_mensagem,usuario=usuario)
    session.add(mensagem)
    session.commit()
    session.close()


def trazer_historico_mensagens():
    session = get_session()
    hist = session.query(Mensagem).all()
    session.close()
    historico = ''
    for mensagem in hist:
        historico += f'\n{mensagem.usuario}: {mensagem.dado}'
    return historico


#mostra_todos_usuarios(session)
#autenticar_usuario(session, 'usuario01', 'senha01')
#inserir_usuario('usuario02', 'senha02')
#inserir_usuario('usuario04', 'senha04')

# inserir_nova_mensagem('Segunda mensagem de teste no histórico', 'usuario02')
#trazer_historico_mensagens(session)


# busca(session,'usuario03')
# usuarios = busca(session, 'usuario03')
# mostra_todos_usuarios(usuarios)
# session.query(User).filter(User.name == 'Emily Faccin').delete()