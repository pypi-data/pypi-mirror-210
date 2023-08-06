from tkinter import Frame

from tkfly.metro._winforms import FlyMetroWidget, FlyMetroFrame

from tkfly.metro.button import FlyMetroButton
from tkfly.metro.checkbox import FlyMetroCheckBox
from tkfly.metro.combobox import FlyMetroComboBox
from tkfly.metro.core import *
from tkfly.metro.datetime import FlyMetroDateTime
from tkfly.metro.label import FlyMetroLabel
from tkfly.metro.progressbar import FlyMetroProgressBar
from tkfly.metro.radiobutton import FlyMetroRadioButton
from tkfly.metro.text import FlyMetroText
from tkfly.metro.tile import FlyMetroTile
from tkfly.metro.togglebox import FlyMetroToggleBox
from tkfly.metro.tooltip import FlyMetroToolTip
from tkfly.metro.trackbar import FlyMetroTrackBar


class FlyMetroTkFrame(Frame):
    def configure(self, **kwargs):
        if "theme" in kwargs:
            style = kwargs.pop("theme")
            if style == "light":
                self.configure(background="#ffffff")
            elif style == "dark":
                self.configure(background="#111111")
        super().configure(**kwargs)


if __name__ == '__main__':
    from tkinter import Tk, Frame

    root = Tk()

    button = FlyMetroButton()
    button.pack()

    root.mainloop()