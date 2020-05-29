import sys
# recebe o IP dos servidores pela linha de comando no momento de rodar o app
try:
    SERVER_IP = sys.argv[1]
except:
    raise AttributeError('IP do servidor não informado')

import kivy
from kivy.app import App
from kivy.clock import Clock
import os
import socket
import pickle
import hashlib

import login_conn as lg
import chat_client
import login_client
import file_client

from kivy.config import Config
Config.set('graphics','resizable',1)
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 450)
Config.set('graphics', 'top',  35)

from kivy.core.window import Window
Window.size = (500, 650)

from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.factory import Factory
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior

# variavel global que irá guardar o usuario utilizando o app
usuario = ''
# porta definida para o servidor de mensagens
PORT = 1234


# definição dos métodos da tela login
class Login(Screen):

    # função chamada no momento de conectar no app
    # autentica usuario e conecta no servidor de msg
    def conectar(self, _):
        # porta definida no início do script 
        porta = PORT
        # ip passado na linha de comando
        ip = SERVER_IP
        # o que for feito na variavel usuario tera escopo global
        global usuario
        # usuario recebe o texto preenchido no campo, na tela gráfica
        usuario = self.ids.txt_usuario.text
        # senha recebe o texto preenchido no campo, na tela gráfica
        senha = self.ids.txt_senha.text

        # faz o hash da senha recebida e trabalha somente com ele
        sh = hashlib.sha1()
        sh.update(senha.encode('utf-8'))
        senha = sh.hexdigest()

        # A vai como cabeçalho para autenticar
        status = login_client.send(f'A:{usuario}:{senha}')
        # se o status recebido foi 200, usuario autenticado e pode prosseguir
        if status == '200':
            # se a função connect aplicada ao socket chat_cliente retornar falso,
            # função para aqui, mostrando o erro na pagina de info
            if not chat_client.connect(ip, porta, usuario, mostrar_erro):
                return
            # limpa os campos usuario e senha na tela
            self.ids.txt_usuario.text = ''
            self.ids.txt_senha.text = ''
            # a tela de chat não foi instanciada até esse ponto, ela é criada aqui
            chatApp.criar_pagina_de_chat()
            # screen manager troca a screen pra tela de chat
            chatApp.screen_manager.current = 'chat'
            # chama a função inicio_chat_historico() pra colocar na tela de chat
            # o historico de mensagens no banco
            chatApp.screen_manager.get_screen(name='chat').inicio_chat_historico()
        # se o status recebido foi 401, usuario e senha não batem
        elif status == '401':
            # cria um popup com uma mensagem de erro e mostra na tela 
            senha_incorreta = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Senha incorreta.\nTente novamente',
                font_size=20))
            senha_incorreta.open()
        # se o status recebido foi 404, o usuario não existe
        elif status == '404':
            # cria um popup com uma mensagem de erro e mostra na tela 
            nao_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário não cadastrado.\nRegistre-se',
                font_size=20))
            nao_cadastrado.open()

    # função que encerra o app rodando
    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()


    # função que basicamente espera um pouquinho e chama conectar
    def join_button(self, instancia):
        Clock.schedule_once(self.conectar, 1)


# definição dos métodos da tela de cadastro de usuarios
class CadastroUsuarios(Screen):
    # limpa os campos da tela e volta pra tela de login
    def voltar_login(self):
        chatApp.screen_manager.current = 'login'
        self.ids.txt_cadastro_usuario.text = ''
        self.ids.txt_cadastro_senha01.text = ''
        self.ids.txt_cadastro_senha02.text = ''


    # função para cadastrar novo usuario
    def cadastrar_usuario(self):
        # recebe o conteudo do campo usuario preenchido na tela
        usuario = self.ids.txt_cadastro_usuario.text
        # recebe o conteudo do campo senha preenchido na tela
        senha = self.ids.txt_cadastro_senha01.text
        # recebe o conteudo do campo confirme sua senha preenchido na tela
        confirm_senha = self.ids.txt_cadastro_senha02.text

        # se qualquer um dos campos estiver em branco, cria um popup com uma
        # mensagem de erro e mostra na tela 
        if usuario.strip() == '' or senha.strip() == '' or confirm_senha.strip():
            em_branco = Popup(title='Preencha todos os campos!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Campos usuário / senha\nnão podem ser vazios',
                font_size=20))
            em_branco.open()
            # sai da função
            return

        # se a senha e a confirmação de senha digitados forem divergentes,
        # cria um popup com uma mensagem de erro e mostra na tela 
        if senha != confirm_senha:
            senha_dif = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='As senhas digitadas\nnão coincidem',
                font_size=20))
            senha_dif.open()
        # caso contrario, tudo certo. podemos inserir
        else:
            # I vai como cabeçalho para inserir
            # status vai ser recebido após execução da função
            status = login_client.send(f'I:{usuario}:{senha}')
            # se o status recebido foi ok
            if status == '200':
                # cria um popup com uma mensagem de sucesso e mostra na tela 
                cadastro_ok = Popup(title='Sucesso!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário cadastrado com\nsucesso. Faça o login',
                font_size=20))
                cadastro_ok.open()
            # status de erro
            elif status == '409':
                # cria um popup com uma mensagem de erro e mostra na tela 
                ja_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário já cadastrado\nResete sua senha se\nnecessario',
                font_size=20))
                ja_cadastrado.open()
            # chama a função pra voltar pra tela de login
            self.voltar_login()


# definição dos métodos da tela alteração de usuarios
class AlteraUsuarios(Screen):
    # limpa os campos da tela e volta pra tela de login
    def voltar_login(self):
        chatApp.screen_manager.current = 'login'
        self.ids.txt_altera_usuario.text = ''
        self.ids.txt_altera_senha01.text = ''
        self.ids.txt_altera_senha02.text = ''

    
    # função que faz o job
    def resetar_senha(self):
        # pega o nome do usuario preenchido na tela
        usuario = self.ids.txt_altera_usuario.text
        # pega a nova senha preenchida na tela
        nova_senha = self.ids.txt_altera_senha01.text
        # pega a confirmação de nova senha preenchida na tela
        confirm_nova_senha = self.ids.txt_altera_senha02.text
        # faz o hash da nova senha
        sh = hashlib.sha1()
        sh.update(nova_senha.encode('utf-8'))
        nova_senha = sh.hexdigest()
        # faz o hash da confirmação nova senha
        sh = hashlib.sha1()
        sh.update(nova_senha.encode('utf-8'))
        confirm_nova_senha = sh.hexdigest()

        # se as senhas digitadas forem diferentes
        # cria um popup com uma mensagem de erro e mostra na tela 
        if nova_senha != confirm_nova_senha:
            senha_dif = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='As senhas digitadas\nnão coincidem',
                font_size=20))
            senha_dif.open()
        # caso contrario, as senhas são iguais
        else:
            # status vai receber o retorno do socket server pra ca
            # no socket server dependendo do cabeçalho ele sabe qual função executar
            status = login_client.send(f'R:{usuario}:{nova_senha}')
            # usuario ecziste faz update no banco
            if status == '200':
                # cria um popup com msg de sucesso
                reset_ok = Popup(title='Sucesso!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Senha resetada com\nsucesso. Faça o login',
                font_size=20))
                reset_ok.open()
            # usuario digitado no ecziste
            elif status == '404':
                # cria um popup com uma mensagem de erro e mostra na tela 
                nao_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário não cadastrado\nCadastre-se',
                font_size=20))
                nao_cadastrado.open()
            # volta pra tela de login
            self.voltar_login()            


# definição dos métodos da tela de chat
class ChatLayout(Screen):
    # inicializa os objetos
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)


    # função que fecha os popups
    def dismiss_popup(self):
        self._popup.dismiss()


    # função que traz o historico de msgs do bd e põe na tela
    def inicio_chat_historico(self):
        global usuario
        # H: history (cabecalho), usuario logado 
        dados = ['H', usuario]
        # msg vai receber a serialização do conteudo de dados
        msg = pickle.dumps(dados)
        # resultado vai receber o retorno do socket server para ca
        resultado = file_client.send(msg)
        # status vai receber a desserialização do resultado recebido
        # é o histórico de mensagens
        status = pickle.loads(resultado)
        # adiciona ao TextInput na tela o conteudo de status
        self.ids.history.text = status


    # função que adiciona no TextInput contendo o historico cada msg enviada
    def adiciona_chat_historico(self, mensagem):
        self.ids.history.text += f'\n{mensagem}'


    # função que lida com o envio de mensagens
    def enviar_mensagem(self):
        try:
            # pega o conteudo do campo na tela com a msg que o usuario quer mandar
            nova_msg = self.ids.nova_mensagem.text
            # limpa o campo
            self.ids.nova_mensagem.text = ''
            # se de fato tem uma mensagem e o usuario não clicou sem querer em enviar
            if nova_msg:
                # manda para o server de chat nossa nova mensagem
                # o resto é tratado por lá
                chat_client.send(nova_msg)
        
        except AttributeError as e:
            print(e)


    # função que exibe o explorer de arquivos como um popup
    def show_load(self):
        # o conteúdo é um objeto do tipo LoadDIalog
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Enviar Arquivo", content=content,
                            size_hint=(0.7, 0.7))
        self._popup.open()


    # assim que clicar em Abrir, deve ser enviado o arquivo via socket
    # para ser guardado no banco, caso dê certo a gravação retorna uma msg
    # com status ok e é enviada uma mensagem automatica para os usuarios do chat
    def load(self, path, filename):
        # variavel global
        global usuario
        # pega o arquivo selecionado pelo usuario como "readbytes" com o apelido stream 
        with open(os.path.join(path, filename[0]), 'rb') as stream:
            # armazena a leitura do arquivo
            arquivo = stream.read()
            # pega o nome do arquivo
            nome = stream.name.split('\\')[-1]
            # P: post (cabecalho), usuario que enviou o arquivo, nome do arquivo, binario 
            dados = ['P', usuario, nome, arquivo]
             # msg vai receber a serialização do conteudo de dados
            msg = pickle.dumps(dados)
            # resultado vai receber o retorno do socket server para ca
            resultado = file_client.send(msg)
            # status vai receber a desserialização de resultado, é o status da op
            status = pickle.loads(resultado)
            # se o status for ok, envia uma mensagem no chat informando
            if status == '200':
                chat_client.send(f'enviou um novo arquivo')
        # fecha o popup de upload
        self.dismiss_popup()


    # função chamada para abrir o popup contendo a tabela com os arquivos no bd
    def show_abrir(self):
        # o conteudo é um objeto do tipo TabelaArquivos que no seu construtor lida
        # com a parte de criar uma tabela, fazer o select no banco e mostrar
        content = TabelaArquivos(cancel=self.dismiss_popup)
        self._popup = Popup(title="Baixar arquivo", content=content,
                            size_hint=(0.7, 0.7))
        self._popup.open()
    
    
    # função de download de documentos do bd
    def download(self, nome):
        # variavel global
        global usuario
        # D: download (cabeçalho), usuario logado, nome do arquivo que será
        # baixado (extraído do botão clicado)
        dado = ['D', usuario, nome]
        # msg vai receber a serialização do conteudo de dados
        msg = pickle.dumps(dado)
        # retorno vai receber o retorno do socket server para ca
        retorno = file_client.send(msg)
        # despickle vai receber o retorno do socket server para ca
        despickle = pickle.loads(retorno)
        # arquivos vai receber a desserialização do retorno, e pega somente o 
        # campo "binario"
        # esperado: binario do arquivo salvo no bd
        arquivo = despickle.binario
        # diretorio vai receber o retorno da função dirname de dirname desse módulo
        # ou seja, ele vai identificar o caminho absoluto onde o módulo está e
        # voltará dois níveis
        diretorio = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # com a pasta onde desejamos salvar os arquivos, basta indicar o nome da
        # pasta que gostaríamos de criar para conter esses arquivos e junta-los
        # com os.join
        diretorio = os.path.join(diretorio, 'viarede_arquivos')
        # caso o diretorio não exista, é criado um diretorio
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
        # define o arquivo
        FILE_PATH = os.path.join(diretorio, nome)
        # com o arquivo aberto como "write bytes", com o apelido f
        with open(FILE_PATH, 'wb') as f:
            # "escreve" em f o binario contido em arquivo
            f.write(arquivo)
        # fecha o popup que contem os a tabela de documentos
        self.dismiss_popup()


    # desloga do chat
    def logout(self):
        # envia uma msg em branco para desconectar o socket do servidor
        chat_client.send('')
        # remove do screen manager a tela de chat criada
        chatApp.screen_manager.remove_widget(chatApp.screen_manager.get_screen('chat'))
        # muda a tela atual do screen manager para login
        chatApp.screen_manager.current = 'login'


# definição dos métodos da tela tabela de arquivos
class TabelaArquivos(FloatLayout):
    # inicialização dos objetos que conterão a lista de arquivos
    # disponibilizados na tabela arquivos e botão cancelar
    items = ListProperty([])
    cancel = ObjectProperty(None)

    # quando um objeto TabelaArquivos for instanciado, chama
    # a função abrir que criará uma tabela com o resultado
    # de um select* na tabela de arquivos
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.abrir()

    # função chamada ao abrir a tabela de arquivos no bd
    # disponiveis para download
    def abrir(self):
        # variavel global
        global usuario
        # G: get, usuario logado
        dados = ['G', usuario]
        # msg vai receber a serialização do conteudo de dados
        msg = pickle.dumps(dados)
        # resultado vai receber o retorno do socket server para ca
        resultado = file_client.send(msg)
        # arquivos vai receber a desserialização do resultado
        # esperado: lista com objetos arquivo
        arquivos = pickle.loads(resultado)

        # itera sobre os objetos arquivo trazidos
        for arquivo in arquivos:
            # itera sobre as colunas em cada arquivo
            for coluna in arquivo:
                # insere na lista que sera mostrada na tabela
                self.items.append(coluna)


    # função de fechamento dos popups
    def dismiss_popup(self):
        self._popup.dismiss()


# adiciona selection e focus behavior à view
class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


# adiciona o suporte à selection ao Button
class SelectableButton(RecycleDataViewBehavior, Button):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)


    # identifica e lida com mudanças na view
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)


    # adiciona selection ao evento on touch down
    def on_touch_down(self, touch):
        if super(SelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)


    # Responde à selection dos itens na view
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


    # define o evento on_press dos botões na tabela de arquivos para download
    def on_press(self):
        # pega a instancia do app rodando
        app = App.get_running_app()
        # usa o screen manager para encontrar a tela chat e utiliza a função 
        # download
        app.screen_manager.get_screen(name='chat').download(self.text)


# definição dos métodos da tela explorer para upload de arquivos
class LoadDialog(FloatLayout):
    # inicializa os objetos que conterão as funções load e
    # cancel do explorer de upload de arquivos
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


# definição dos métodos da tela de info
class InfoPage(Screen):

    # Atualiza a mensagem exibida na tela de info
    def update_info(self, message):
        self.ids.textao.text = message


# definição dos métodos do app
class Test(App):
    # contrutor do app
    def build(self):
        # define o icone
        self.icon = 'icon.jpeg'
        # define o title
        self.title = 'Login - VIA REDE'
        # instancia um screen manager pra lidar com as diferentes telas
        self.screen_manager = ScreenManager()
        # instancia uma tela de login e adiciona ao screen manager
        self.screen_manager.add_widget(Login(name='login'))
        # instancia uma tela de cadastro e adiciona ao screen manager
        self.screen_manager.add_widget(CadastroUsuarios(name='cadastro'))
        # instancia uma tela de alteração de usuario e adiciona ao screen manager
        self.screen_manager.add_widget(AlteraUsuarios(name='altera'))

        # instancia uma tela de chat e adiciona ao screen manager
        # fazer dessa forma nos possibilita ter uma variavel que guarda
        # a instancia do objeto infopage, podendo ser referenciado
        self.info_page = InfoPage()
        screen = Screen(name='info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        # utilizado pelo FIleChooser para os explorer de upload e download
        # de documentos
        Factory.register('ChatLayout', cls=ChatLayout)
        Factory.register('LoadDialog', cls=LoadDialog)

        return self.screen_manager


    # instancia uma tela de chat e adiciona ao screen manager
    def criar_pagina_de_chat(self):
        self.screen_manager.add_widget(ChatLayout(name='chat'))


    # instancia a tela tabela de arquivos e adiciona ao screen manager
    def criar_tabela_arquivos(self):
        # instancia um objeto do tipo TabelaArquivos 
        self.tabela = TabelaArquivos()
        # cria uma screen e nomeia como arquivos
        screen = Screen(name='arquivos')
        # adiciona a screen o objeto TabelaArquivos
        screen.add_widget(self.tabela)
        # adiciona ao screen manager a screen
        self.screen_manager.add_widget(screen)


# função que mostra uma mensagem de erro na pagina de info
def mostrar_erro(message):
    # chama a função update_info com a mensagem passada
    chatApp.info_page.update_info(message)
    # screen manager muda a tela atual para a tela de info
    chatApp.screen_manager.current = 'info'
    # espera 10 segundos e encerra o app
    Clock.schedule_once(sys.exit, 10)



if __name__ == '__main__':
    # instancia um objeto app
    chatApp = Test()
    # roda o app
    chatApp.run()
