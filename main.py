import kivy 
from kivy.app import App

from kivy.config import Config
Config.set('graphics','resizable',0)
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 450)
Config.set('graphics', 'top',  70)

from kivy.core.window import Window
Window.size = (500, 650)

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image

class TalkLayout(BoxLayout):
    pass

class FirstLayout(BoxLayout):

    def fechar_app(self):
        App.get_running_app().stop()
        Window.close()

class Test(App):
    def build(self):
        self.icon = 'icon.jpeg'
        self.title = 'Login - VIA REDE'
        return FirstLayout()

if __name__ == '__main__':
    Test().run()
