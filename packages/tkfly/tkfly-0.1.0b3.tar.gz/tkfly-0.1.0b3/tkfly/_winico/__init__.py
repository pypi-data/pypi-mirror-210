from tkfly._winico.load import load_winico
from tkfly._winico.command import *


ADD = "add"
MODIFY = "modify"
DELETE = "delete"

APPLICATION = "application"
ASTERISK = "asterisk"
ERROR = "error"
EXCLAMATION = "exclamation"
HAND = "hand"
QUESTION = "question"
INFORMATION = "information"
WARNING = "warning"
WINLOGO = "winlogo"

SMALL = "small"
BIG = "big"

MESSAGE = "%m"
ID = "%i"
X = "%x"
Y = "%y"
TIME = "%t"

WM_MOUSEMOVE = "WM_MOUSEMOVE"
WM_LBUTTONDOWN = "WM_LBUTTONDOWN"
WM_LBUTTONUP = "WM_LBUTTONUP"
WM_LBUTTONDBLCLK = "WM_LBUTTONDBLCLK"
WM_RBUTTONDOWN = "WM_RBUTTONDOWN"
WM_RBUTTONUP = "WM_RBUTTONUP"
WM_RBUTTONDBLCLK = "WM_RBUTTONDBLCLK"
WM_MBUTTONDOWN = "WM_MBUTTONDOWN"
WM_MBUTTONUP = "WM_MBUTTONUP"
WM_MBUTTONDBLCLK = "WM_MBUTTONDBLCLK"

if __name__ == '__main__':
    import tkinter as tk

    Window = tk.Tk()


    def CallBack(Message, X, Y):
        if Message == WM_RBUTTONDOWN:
            Menu = tk.Menu(tearoff=False)
            Menu.add_command(label="Quit", command=Window.quit)
            Menu.tk_popup(X, Y)


    taskbar(ADD, load(APPLICATION), (Window.register(CallBack), MESSAGE, X, Y))

    Window.mainloop()