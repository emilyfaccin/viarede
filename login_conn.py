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

# encode = utf-8

# criando a engine - comunicação com o banco
# echo=True indica que será printado no console o comando real executado
engine = create_engine('sqlite:///viarede.db', echo=True, poolclass=NullPool)
# cria uma session conectada à nossa engine
Session = sessionmaker(bind=engine)


# Para usar a ORM precisamos de uma sessão
def get_session():
    # instancia uma sessão e a retorna
    session = Session()
    return session

# Base declarativa: usada para a ORM
# Permite criação e querys através de classes, sem SQL
Base = declarative_base()


# representacao da tabela usuario
class Usuario(Base):
    # nome real da tabela no banco
    __tablename__ = 'usuarios'

    # coluna nome, string, chave primaria
    name = Column(String, primary_key=True)
    # coluna senha, string
    password = Column(String)
    # indica o relacionamento com a tabela mensagem
    mensagem = relationship('Mensagem', backref='usuarios')
    # indica o relacionamento com a tabela arquivo
    arquivo = relationship('Arquivo', backref='usuarios')

    # indica a representação do objeto
    def __repr__(self):
        return f'User {self.name}'


# representacao da tabela mensagem   
class Mensagem(Base):
    # nome real da tabela no banco
    __tablename__ = 'mensagens'

    # coluna id, inteiro, chave primeira
    id = Column(Integer, primary_key=True)
    # coluna dado, string, vai guardar o conteudo da mensagem
    dado = Column(String)
    # # coluna usuario, string, chave estrangeira do usuario que enviou a msg
    usuario = Column(String, ForeignKey('usuarios.name'), nullable=False)
    # indica o relacionamento com a tabela usuario
    user = relationship('Usuario')

    # indica a representação do objeto
    def __repr__(self):
        return f'Mensagem {self.dado}'

# representacao da tabela arquivo
class Arquivo(Base):
    # nome real da tabela no banco
    __tablename__ = 'arquivos'

    # coluna id, inteiro, chave primaria
    id = Column(Integer, primary_key=True)
    # coluna nome, string, nome do arquivo
    nome = Column(String)
    # coluna binario, LargeBinary, vai guardar o binario do arquivo 
    binario = Column(LargeBinary)
    # coluna nome do usuario, string, chave estrangeira do usuario que enviou o arquivo
    usuario = Column(String, ForeignKey('usuarios.name'), nullable=False)
    # indica o relacionamento com a tabela usuario
    user = relationship('Usuario')

    # indica a representação do objeto
    def __repr__(self):
        return f'Arquivo {self.nome}'


# Função que cria o banco. Usada uma vez só
#Base.metadata.create_all(engine)


# função que busca todos os usuarios do banco por nome
def busca(nome):
    # cria uma sessão
    session = get_session()
    # dados vai receber todos os resultados da query (select), filtrados pelo nome
    # passado como parametro. resultado é uma lista de objetos usuario
    dados = session.query(Usuario).filter_by(name=nome).all()
    # encerra a sessão
    session.close()
    # retorna a lista de usuarios
    return dados


# função que itera sobre os usuarios e printa no console
# apenas para debug
def mostra_todos_usuarios():
    # cria uma sessão
    session = get_session()
    # variável vai receber o resultado da query (select *) da tabela usuario
    lista_usuarios = session.query(Usuario).all()
    # itera sobre a lista e printa no console em forma de dicionario
    for usuario in lista_usuarios:
        print(usuario.__dict__)
    # encerra a sessão
    session.close()


# função que insere um novo usuario no banco
def inserir_usuario(usuario, senha):
    # cria uma sessão
    session = get_session()
    # efetua o hash da senha pra guardar no banco o valor hashado
    sh = hashlib.sha1()
    sh.update(senha.encode('utf-8'))
    # valor que de fato será armazenado no banco
    hash_value = sh.hexdigest()
    # instancia um objeto usuario com os dados nome e senha passados como parametro 
    user = Usuario(name=usuario, password=hash_value)
    # tenta
    try:
        # função de insert
        session.add(user)
        # commita as mudanças
        session.commit()
        # retorna o status 200, indicando o sucesso da operação
        return '200'
    # caso essa exceção seja levantada, sabemos que tentamos inserir um usuario que já
    # existe, tratar isso
    except IntegrityError as e:
        # 409 conflict
        return '409'
    # executa sempre
    finally:
        # encerra a sessão
        session.close()
    

# função que altera a senha de um usuario (reset de senha)
def alterar_usuario(nome, senha):
    # cria uma sessão
    session = get_session()
    # tenta
    try:
        # retorna o resultado da query (select) na tabela usuario passando nome
        # no where. como nome é chave primaria vai retornar somente uma correspondencia
        usuario = session.query(Usuario).filter(Usuario.name == nome).one()
        # altera o campo senha do usuario pesquisado para a senha enviada como parametro
        # (hashada)
        usuario.password = senha
        # comita as alterações
        session.commit()
        # retorna o status 200, indicando o sucesso da operação
        return '200'
    # caso essa exceção seja levantada, o usuario passado não foi encontrado no banco
    except NoResultFound as e:
        # 404 not found
        return '404'
    # executa sempre
    finally:
        # encerra a sessão
        session.close()


# função de autenticação de usuario
def autenticar_usuario(usuario, senha):
    try:
        # lista recebe o resultado da função busca passando como parametro o usuario (PK)
        # resultado é uma lista de 1 objeto correspondente à busca
        lista = busca(usuario)
        # transforma o resultado de lista para objeto pessoa
        pessoa = lista[0]
        # variavel usuario guarda o nome da pessoa trazida do bd
        user = pessoa.name
        # variavel passwd guarda a senha trazida do bd 
        passwd = pessoa.password

        # se o usuario passado for igual ao trazido do banco e o hash da senha passada seja
        # igual ao hash no bd, usuario existe e informou senha valida
        if usuario == user and senha == passwd:
            # retorna o status 200, indicando o sucesso da operação
            return '200'
        else:
            # retorna o status 401, unauthorized
            return '401'
    # essa exceção é levantada quando há erro de index, logo, usuario informado não foi encontrado
    except IndexError as e:
        # 404 not found
        return '404'


# como utilizamos o mesmo servidor para autenticação, inserção e reset de senha
# a diferenciação da operação é feita através do cabeçalho (id), sempre enviado junto
def triagem(id, usuario, senha):
    # A = autenticar
    # I = inserir
    # R = resetar senha
    # se o id enviado for A, queremos autenticar
    if id == 'A':
        # recebe o status da operação
        status = autenticar_usuario(usuario, senha)
    # se o id enviado for I, queremos inserir
    elif id == 'I':
        # recebe o status da operação
        status = inserir_usuario(usuario, senha)
    # se o id enviado for R, queremos resetar senha
    elif id == 'R':
        # recebe o status da operação
        status = alterar_usuario(usuario, senha)
    # retorna o conteúdo de status
    return status


# função que insere nova mensagem no bd
def inserir_nova_mensagem(nova_mensagem, usuario):
    # cria uma sessão
    session = get_session()
    # instancia um novo objeto mensagem com o conteudo da msg e usuario que enviou recebidas
    # como parametro. a coluna id é autoincrementável
    mensagem = Mensagem(dado=nova_mensagem,usuario=usuario)
    # adiciona a noma mensagem no banco
    session.add(mensagem)
    # comita as alterações
    session.commit()
    # encerra a sessão
    session.close()


# função que faz um select* na tabela mensagens para exibir o historico de mensagens
def trazer_historico_mensagens():
    # cria uma sessão
    session = get_session()
    try:
        # variavel receberá o resultado da query (select*) na tabela mensagens, lista de obj
        hist = session.query(Mensagem).all()
        # inicializa variável histórico
        historico = ''
        # itera sobre os objetos mensagem selecionados
        for mensagem in hist:
            # armazena na variavel acumuladora historico o campo usuario e campo dado de cada mensagem
            historico += f'\n{mensagem.usuario}: {mensagem.dado}'
        # retorna a variavel historico
        return historico
    except:
        # 404 not found
        return '404'
    finally:
        # encerra a sessão
        session.close()


# como utilizamos o mesmo servidor para consulta, inserção e download de arquivos,
# além do historico de msgs a diferenciação da operação é feita através do cabeçalho),
# sempre enviado junto
def triagem_arquivos(cabecalho, user, name=None, binary=None):
    # G = GET
    # P = POST
    # D = DOWNLOAD
    # H = HISTORY
    # se o id enviado for G, queremos a lista de arquivos
    if cabecalho == 'G':
        # recebe o status da operação
        status = get_arquivos()
    # se o id enviado for P, queremos gravar um arquivo no bd
    elif cabecalho == 'P':
        # recebe o status da operação
        status = gravar_arquivo(nome=name, binario=binary, usuario=user)
    # se o id enviado for D, queremos um arquivo especifico para download
    elif cabecalho == 'D':
        # recebe o status da operação
        status = acessa_arquivo_por_nome(name)
    # se o id enviado for H, queremos o historico de mensagens
    elif cabecalho == 'H':
        # recebe o status da operação
        status = trazer_historico_mensagens()
    # retorna o status
    return status


# função que insere um novo arquivo no bd
def gravar_arquivo(nome, binario, usuario):
    # cria uma nova sessão
    session = get_session()
    try:
        # instancia um objeto arquivo com nome do arquivo, binario e usuario
        # que enviou passados como parametro
        arquivo = Arquivo(nome=nome, binario=binario, usuario=usuario)
        # # adiciona as mudanças no bd
        session.add(arquivo)
        # comita as mudanças no banco
        session.commit()
        return '200'
    except:
        # 400, bad request
        return '400'
    finally:
        # encerra a sessão
        session.close()


# função que retorna uma lista com todos os arquivos no bd
def get_arquivos():
    # cria uma sessão
    session = get_session()
    # lista com todos os arquivos no bd
    arquivos = session.query(Arquivo.nome).all()
    # encerra a sessão
    session.close()
    # retorna a lista
    return arquivos


# função que executa select na tabela arquivos por nome do arquivo
# utilizada na função de download de arquivos
def acessa_arquivo_por_nome(nome):
    # cria uma sessão
    session = get_session()
    # variável arquivo vai receber o resultado da query (select where nome=nome) e
    # e trará um resultado
    arquivo = session.query(Arquivo).filter_by(nome=nome).one()
    # retorna o objeto arquivo
    return arquivo
