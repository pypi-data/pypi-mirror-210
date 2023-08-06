import PySimpleGUI as sg
from hashlib import md5
import os
import sys

# import winsound as ws
import threading

global sair
sair = False

brasil_dict = {
    "cancel": "Cancelar",
    "password": "senha",
    "check": "verificar",
    "start": "começar",
    "continue": "continuar",
    "stop": "parar",
    "process": "processo",
    "try again": "tentar novamente",
    "type the path": "insira o endereço do arquivo",
}


def get_brasil_word(word):
    return brasil_dict[word]


def get_english_word(word):
    return word.capitalize()


def get_getter_lenguage(abrev):
    if abrev == "pt":
        return get_brasil_word
    return get_english_word


def soundFunc(f):
    def auxF():
        global sair
        sair = False
        for i in range(1000):
            if sair:
                break
            # acrecimo = 0 if i % 2 else f
            # ws.Beep(f + acrecimo, 500)

    return auxF


def playSound(soundF):
    threading.Thread(target=soundF).start()


def stopSound():
    global sair
    sair = True


class Layouts:
    def __init__(self, translated):
        self.password = [
            [
                sg.Text(f'{translated("password")}:'),
                sg.InputText(background_color="#ffffff"),
            ],
            [sg.Button(translated("check")), sg.Button(translated("cancel"))],
        ]

        self.simple = lambda color, text: [sg.Text(text, background_color=color)]

        self.wrong = lambda text: [
            (self.simple(color="red", text=text)),
            ([sg.Button(f'{translated("continue")} {translated("process")}')]),
            ([sg.Button(f'{translated("stop")} {translated("process")}')]),
            ([sg.Button(f'{translated("try again")}')]),
        ]
        self.ok = lambda text: [
            (self.simple(color="green", text=text)),
            ([sg.Button("ok")]),
        ]

        self.getPath = [
            [
                sg.Text(f'{translated("type the path")}:'),
                sg.InputText(background_color="#ffffff"),
                sg.FileBrowse(
                    initial_folder=os.getcwd(), file_types=[("xmls Files", "*.xlsx")]
                ),
            ],
            [sg.Button(translated("start")), sg.Button(translated("cancel"))],
        ]


class Waiters:
    def __init__(self, lenguage, layouts=Layouts):
        translated = get_getter_lenguage(lenguage)
        self.passwordStr = ""
        self.filePath = ""
        self.translated = translated
        self.layouts = layouts(translated)
        self.translated = translated

    def password(self, title, correctHash):
        window = sg.Window(title).Layout(self.layouts.password)
        while True:
            event, values = window.read()
            self.passwordStr = values[0].replace('"', "")
            userPasswordmd5 = md5(self.passwordStr.encode()).hexdigest()

            if event == sg.WIN_CLOSED or event == self.translated("cancel"):
                window.close()
                sys.exit()
            if (
                event == self.translated("check") and userPasswordmd5 == correctHash
            ):  # if user closes window or clicks cancel
                window.close()
                break

    def ok(self, title, text="its ok"):
        playSound(soundFunc(800))
        window = sg.Window(title).Layout(self.layouts.ok(text=text))
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "ok":
                break
        stopSound()
        window.close()

    def wrong(self, text, title="erro"):
        playSound(soundFunc(500))
        window = sg.Window(title).Layout(self.layouts.wrong(text=text))
        while True:
            event, values = window.read()
            if (
                event == sg.WIN_CLOSED
                or event == f'{self.translated("stop")} {self.translated("process")}'
            ):
                stopSound()
                window.close()
                sys.exit()
            if event == f'{self.translated("continue")} {self.translated("process")}':
                stopSound()
                window.close()
                return {"tryAgain": False}
            if event == self.translated("try again"):
                stopSound()
                window.close()
                return {"tryAgain": True}

    def getPath(self, title="digite o caminho"):
        window = sg.Window(title).Layout(self.layouts.getPath)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == self.translated("cancel"):
                window.close()
                sys.exit()
            if event == self.translated("start"):
                path = values[0].replace('"', "")
                break

        window.close()
        return path


gui = Waiters("pt")
