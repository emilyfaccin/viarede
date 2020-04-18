import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

kivy.require('1.11.1')



class LoginApp(App):
    def build(self):
        return Label(text='Olá enfermeira')

# Rodando o app
if __name__ == '__main__':
    LoginApp().run()
