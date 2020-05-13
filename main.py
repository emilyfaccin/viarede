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
# try:
#     SERVER_IP = sys.argv[1]
# except:
#     raise AttributeError('IP do servidor não informado')
SERVER_IP = '192.168.56.1'


class Login(Screen):


    def conectar(self, _):
        porta = PORT
        ip = SERVER_IP
        usuario = self.ids.txt_usuario.text
        senha = self.ids.txt_senha.text

        # A vai como cabeçalho para autenticar
        status = login_client.send(f'A:{usuario}:{senha}')
        if status == '200':
            print('Sweet success')

            if not chat_client.connect(ip, porta, usuario, mostrar_erro):
                return

            chatApp.criar_pagina_de_chat()
            chatApp.screen_manager.current = 'chat'

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

    # mudar de acesso direto ao banco para através do server
    # def inicio_chat_historico(self):
    #     self.ids.history.text = lg.trazer_historico_mensagens()

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
        self.screen_manager.add_widget(AlteraUsuarios(name='altera'))

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
