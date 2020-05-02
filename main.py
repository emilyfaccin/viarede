import kivy 
from kivy.app import App

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

class ChatLayout(BoxLayout):
    pass


class Login(Screen):
    
    def cancelar_cadastro():
        pass


    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()


class CadastroUsuarios(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file('test.kv')

class Test(App):
    def build(self):
        self.icon = 'icon.jpeg'
        self.title = 'Login - VIA REDE'
        return kv


if __name__ == '__main__':
    chatApp = Test()
    chatApp.run()
