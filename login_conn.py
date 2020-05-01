import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import hashlib

# encode = utf-8


# criando a engine - comunicação com o banco
# echo=True indica que será printado no console o comando real executado
engine = create_engine('sqlite:///viarede.db', echo=True)

# Para usar a ORM precisamos de uma sessão
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# representacao da tabela usuario
class User(Base):
    __tablename__ = 'users'

    name = Column(String, primary_key=True)
    password = Column(String)

    def __repr__(self):
        return f'User {self.name}'
    
    # @classmethod
    # def busca_por_nome(cls, session, name):
    #     return session.query(cls).filter_by(name=name).all()

# Base.metadata.create_all(engine) em tese não preciso mais disso


def busca(session, nome):
    dados = session.query(User).filter_by(name=nome).all()
    return dados


def mostra_todos_usuarios(lista_usuarios):
    for usuario in lista_usuarios:
        print(usuario.__dict__)


def inserir_usuario(usuario, senha):
    sh = hashlib.sha1()
    sh.update(senha.encode('utf-8'))
    hash_value = sh.hexdigest()
    user = User(name=usuario, password=hash_value)
    session.add(user)
    session.commit()


def altera_usuario(User, nome, senha):
    update = User.update().\
                where(User.name == nome).\
                values(name=nome, password=senha)


def entrar(session, usuario, senha):
    lista = busca(session,usuario)
    pessoa = lista[0]
    user = pessoa.name
    passwd = pessoa.password

    sh = hashlib.sha1()
    sh.update(senha.encode('utf-8'))
    hash_value = sh.hexdigest()
    
    if usuario == user and hash_value == passwd:
        print('Bem vindo')
    else:
        print('Tente novamente')

# inserir_usuario('usuario03', 'senha03')
# inserir_usuario('usuario02', 'senha02')

busca(session,'usuario03')
usuarios = busca(session, 'usuario03')
mostra_todos_usuarios(usuarios)
# session.query(User).filter(User.name == 'Emily Faccin').delete()