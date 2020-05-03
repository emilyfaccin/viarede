import kivy 
from kivy.app import App
import login_conn
import socket
from kivy.clock import Clock
import socket_client
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

PORT = 1234
PORT_AUTH = 1300


class Login(Screen):

    def ir_cadastro(self):
        chatApp.screen_manager.current = 'cadastro'

    def conectar(self, _):
        porta = PORT
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        usuario = self.ids.txt_usuario.text

        if not socket_client.connect(ip, porta, usuario, mostrar_erro):
            return

        chatApp.criar_pagina_de_chat()
        chatApp.screen_manager.current = 'chat'


    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()


    def join_button(self, instancia):
        porta = PORT
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        usuario = self.ids.txt_usuario.text

        Clock.schedule_once(self.conectar, 1)

class CadastroUsuarios(Screen):
    
    def voltar_login(self):
        chatApp.screen_manager.current = 'login'


class ChatLayout(Screen):
    
    def enviar_mensagem(self):
        print('MENSAGEM!!')


class InfoPage(Screen):

    # Called with a message, to update message text in widget
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
    chatApp.run()
