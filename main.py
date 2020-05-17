import kivy
from kivy.app import App
from kivy.clock import Clock
import sys
import os
import socket
import pickle

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

usuario = ''
PORT = 1234
# try:
#     SERVER_IP = sys.argv[1]
# except:
#     raise AttributeError('IP do servidor não informado')
SERVER_IP = '192.168.56.1'
HEADER = 10


class Login(Screen):


    def conectar(self, _):
        porta = PORT
        ip = SERVER_IP
        global usuario
        usuario = self.ids.txt_usuario.text
        senha = self.ids.txt_senha.text

        # A vai como cabeçalho para autenticar
        status = login_client.send(f'A:{usuario}:{senha}')
        if status == '200':
            print('Sweet success')

            if not chat_client.connect(ip, porta, usuario, mostrar_erro):
                return
            
            self.ids.txt_usuario.text = ''
            self.ids.txt_senha.text = ''

            chatApp.criar_pagina_de_chat()
            chatApp.screen_manager.current = 'chat'
            chatApp.screen_manager.get_screen(name='chat').inicio_chat_historico()

        elif status == '401':
            senha_incorreta = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Senha incorreta.\nTente novamente',
                font_size=20))
            senha_incorreta.open()
            print('Senha inválida. Tente novamente')

        elif status == '404':
            nao_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário não cadastrado.\nRegistre-se',
                font_size=20))
            nao_cadastrado.open()
            print('Usuário não cadastrado')


    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()


    def join_button(self, instancia):

        Clock.schedule_once(self.conectar, 1)


class CadastroUsuarios(Screen):
    
    def voltar_login(self):
        chatApp.screen_manager.current = 'login'
        self.ids.txt_cadastro_usuario.text = ''
        self.ids.txt_cadastro_senha01.text = ''
        self.ids.txt_cadastro_senha02.text = ''


    def cadastrar_usuario(self):
        usuario = self.ids.txt_cadastro_usuario.text
        senha = self.ids.txt_cadastro_senha01.text
        confirm_senha = self.ids.txt_cadastro_senha02.text

        if usuario.strip() == '' or senha.strip() == '':
            em_branco = Popup(title='Preencha todos os campos!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Campos usuário / senha\nnão podem ser vazios',
                font_size=20))
            em_branco.open()
            return

        # I vai como cabeçalho para inserir
        if senha != confirm_senha:
            senha_dif = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='As senhas digitadas\nnão coincidem',
                font_size=20))
            senha_dif.open()
            print('Senhas não conferem')
        else:
            status = login_client.send(f'I:{usuario}:{senha}')
            print(f'{status}')
            if status == '200':
                print('Usuario cadastrado com sucesso')
                cadastro_ok = Popup(title='Sucesso!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário cadastrado com\nsucesso. Faça o login',
                font_size=20))
                cadastro_ok.open()

            elif status == '409':
                print('Usuario ja cadastrado. Resete sua senha se necessario')
                ja_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário já cadastrado\nResete sua senha se\nnecessario',
                font_size=20))
                ja_cadastrado.open()
            self.voltar_login()


class AlteraUsuarios(Screen):

    def voltar_login(self):
        chatApp.screen_manager.current = 'login'
        self.ids.txt_altera_usuario.text = ''
        self.ids.txt_altera_senha01.text = ''
        self.ids.txt_altera_senha02.text = ''

    
    def resetar_senha(self):
        usuario = self.ids.txt_altera_usuario.text
        nova_senha = self.ids.txt_altera_senha01.text
        confirm_nova_senha = self.ids.txt_altera_senha02.text

        # se as senhas digitadas forem diferentes, popup
        if nova_senha != confirm_nova_senha:
            senha_dif = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='As senhas digitadas\nnão coincidem',
                font_size=20))
            senha_dif.open()
            print('Senhas não conferem')
        else:
            status = login_client.send(f'R:{usuario}:{nova_senha}')
            # usuario ecziste faz update no banco
            if status == '200':
                print('Senha resetada com sucesso')
                reset_ok = Popup(title='Sucesso!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Senha resetada com\nsucesso. Faça o login',
                font_size=20))
                reset_ok.open()
            # usuario digitado no ecziste
            elif status == '404':
                print('Usuario não cadastrado. Cadastre-se')
                nao_cadastrado = Popup(title='Atenção!', 
                size_hint=(None, None), size=(300, 300),
                content=Label(text='Usuário não cadastrado\nCadastre-se',
                font_size=20))
                nao_cadastrado.open()
            self.voltar_login()            


class ChatLayout(Screen):

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)


    def dismiss_popup(self):
        self._popup.dismiss()


    def inicio_chat_historico(self):
        global usuario
        dados = ['H', usuario]
        msg = pickle.dumps(dados)
        resultado = file_client.send(msg)
        status = pickle.loads(resultado)
        self.ids.history.text = status


    # def adiciona_chat_historico(self, mensagem):
    #     self.ids.history.text += f'\n{mensagem}'


    def enviar_mensagem(self):
        
        try:
            nova_msg = self.ids.nova_mensagem.text
            self.ids.nova_mensagem.text = ''

            if nova_msg:
                chat_client.send(nova_msg)
        
        except AttributeError as e:
            print(e)

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Enviar Arquivo", content=content,
                            size_hint=(0.7, 0.7))
        self._popup.open()
    

    # assim que clicar em Abrir, deve ser enviado o arquivo via socket
    # para ser guardado no banco, caso dê certo a gravação retorna uma msg
    # com status ok e é enviada uma mensagem automatica pros usuarios do chat
    def load(self, path, filename):
        global usuario
        with open(os.path.join(path, filename[0]), 'rb') as stream:
            arquivo = stream.read()
            nome = stream.name.split('\\')[-1]
            print(stream.name)
            # cabecalho P de post
            dados = ['P', usuario, nome, arquivo]
            msg = pickle.dumps(dados)
            resultado = file_client.send(msg)
            status = pickle.loads(resultado)
            print(status)
            if status == '200':
                chat_client.send(f'enviou um novo arquivo')
        self.dismiss_popup()


    def show_abrir(self):
        content = TabelaArquivos(cancel=self.dismiss_popup)
        self._popup = Popup(title="Baixar arquivo", content=content,
                            size_hint=(0.7, 0.7))
        self._popup.open()
    
    
    def download(self, nome):
        global usuario
        dado = ['D', usuario, nome]
        msg = pickle.dumps(dado)
        retorno = file_client.send(msg)
        despickle = pickle.loads(retorno)
        arquivo = despickle.binario

        diretorio = r'E:\Documents\arquivos_viarede'
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
        with open(f'{diretorio}\\{nome}', 'wb') as f:
            f.write(arquivo)
        self.dismiss_popup()


    def logout(self):
        chat_client.send('')
        chatApp.screen_manager.remove_widget(chatApp.screen_manager.get_screen('chat'))
        chatApp.screen_manager.current = 'login'


class TabelaArquivos(FloatLayout):
    items = ListProperty([])
    cancel = ObjectProperty(None)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.abrir()


    def abrir(self):
        global usuario
        # G: get
        dados = ['G', usuario]
        msg = pickle.dumps(dados)
        resultado = file_client.send(msg)
        arquivos = pickle.loads(resultado)


        for arquivo in arquivos:
            for coluna in arquivo:
                self.items.append(coluna)
        # return arquivos
    
    
    def dismiss_popup(self):
        self._popup.dismiss()


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableButton(RecycleDataViewBehavior, Button):
    ''' Add selection support to the Button '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected

    def on_press(self):
        pass
        app = App.get_running_app()
        app.screen_manager.get_screen(name='chat').download(self.text)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class InfoPage(Screen):

    # Atualiza a mensagem exibida na tela de info
    def update_info(self, message):
        self.ids.textao.text = message


class Test(App):
    def build(self):
        self.icon = 'icon.jpeg'
        self.title = 'Login - VIA REDE'
        
        self.screen_manager = ScreenManager()

        self.screen_manager.add_widget(Login(name='login'))
        self.screen_manager.add_widget(CadastroUsuarios(name='cadastro'))
        self.screen_manager.add_widget(AlteraUsuarios(name='altera'))

        self.info_page = InfoPage()
        screen = Screen(name='info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        Factory.register('ChatLayout', cls=ChatLayout)
        Factory.register('LoadDialog', cls=LoadDialog)


        return self.screen_manager

    def criar_pagina_de_chat(self):
        self.screen_manager.add_widget(ChatLayout(name='chat'))
    

    def criar_tabela_arquivos(self):
        self.tabela = TabelaArquivos()
        screen = Screen(name='arquivos')
        screen.add_widget(self.tabela)
        self.screen_manager.add_widget(screen)


def mostrar_erro(message):
    chatApp.info_page.update_info(message)
    chatApp.screen_manager.current = 'info'
    Clock.schedule_once(sys.exit, 10)



if __name__ == '__main__':
    chatApp = Test()
    chatApp.run()
