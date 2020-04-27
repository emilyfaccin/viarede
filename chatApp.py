import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

kivy.require('1.11.1')

class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.cols = 2

        self.add_widget(Label(text='Usuario:'))

        self.user = TextInput(multiline=False)
        self.add_widget(self.user)

        self.add_widget(Label(text='Senha:'))
        
        self.senha = TextInput(multiline=False)
        self.add_widget(self.senha)

        self.btn_cancelar = Button(text='Cancelar')
        self.add_widget(self.btn_cancelar)

        self.btn_login = Button(text='Login')
        self.btn_login.bind(on_press=self.entrar)
        self.add_widget(self.btn_login)

    def entrar(self, instancia):
        user = self.user.text
        senha = self.senha.text

        info = f'Tentando conectar como {user}'
        chat_app.info_page.update_info(info)

        chat_app.screen_manager.current = 'Info'

class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1

        self.message = Label(halign='center', valign='middle',font_size=30)
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

    def update_info(self, message):
            self.message.text = message

    def update_text_width(self, *_):
            self.message.text_size = (self.message.width*0.9, None)

class ChatApp(App):
    def build(self):
        # screen_manager é um objeto ScreenManager
        self.screen_manager = ScreenManager()
        # connect_page é um objeto ConnectPage
        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

# Rodando o app
if __name__ == '__main__':
    chat_app = ChatApp()
    chat_app.run()
