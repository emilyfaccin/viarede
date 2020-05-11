import kivy 
from kivy.app import App
import login_conn as lg
import socket
from kivy.clock import Clock
import chat_client
import sys
import login_client
import sys

from kivy.config import Config
Config.set('graphics','resizable',0)
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 450)
Config.set('graphics', 'top',  70)

from kivy.core.window import Window
Window.size = (500, 650)

from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView


PORT = 1234
try:
    SERVER_IP = sys.argv[1]
except:
    raise AttributeError('IP do servidor não informado')


class Login(Screen):
    def ir_cadastro(self):
        chatApp.screen_manager.current = 'cadastro'

    def conectar(self, _):
        porta = PORT
        # hostname = socket.gethostname()
        # ip = socket.gethostbyname(hostname)
        ip = SERVER_IP
        usuario = self.ids.txt_usuario.text
        senha = self.ids.txt_senha.text

        status = login_client.send(f'{usuario}:{senha}')
        if status == '200':
            print('Sweet success')

            if not chat_client.connect(ip, porta, usuario, mostrar_erro):
                return

            chatApp.criar_pagina_de_chat()
            chatApp.screen_manager.current = 'chat'

        elif status == '401':
            print('Senha inválida. Tente novamente')

        elif status == '404':
            print('Usuário não cadastrado')


    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()


    def join_button(self, instancia):
        # porta = PORT
        # hostname = socket.gethostname()
        # ip = socket.gethostbyname(hostname)
        # usuario = self.ids.txt_usuario.text

        Clock.schedule_once(self.conectar, 1)


class CadastroUsuarios(Screen):
    
    def voltar_login(self):
        chatApp.screen_manager.current = 'login'


class ChatLayout(Screen):

    # por enquanto não consegui aplicar
    def inicio_chat_historico(self):
        self.ids.history.text = lg.trazer_historico_mensagens()

    def adiciona_chat_historico(self, mensagem):
        self.ids.history.text += f'\n{mensagem}'

    def enviar_mensagem(self):
        
        try:
            nova_msg = self.ids.nova_mensagem.text
            # usuario = 'usuario'
            self.ids.nova_mensagem.text = ''

            # historico = self.ids.history.text
            if nova_msg:
                # novo_historico =  self.ids.history.text + f'{usuario}: {nova_msg}'
                # self.ids.history.text = novo_historico
                # lg.inserir_nova_mensagem(nova_msg, usuario)
                chat_client.send(nova_msg)
        
        except AttributeError as e:
            print(e)



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

        self.info_page = InfoPage()
        screen = Screen(name='info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def criar_pagina_de_chat(self):
        self.screen_manager.add_widget(ChatLayout(name='chat'))

def mostrar_erro(message):
    chatApp.info_page.update_info(message)
    chatApp.screen_manager.current = 'info'
    Clock.schedule_once(sys.exit, 10)

if __name__ == '__main__':
    chatApp = Test()
    from pprint import pprint
    pprint(locals())
    chatApp.run()
