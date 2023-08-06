from Guna.UI2.WinForms import Guna2Button, Guna2ComboBox, \
    Guna2Chip, Guna2CircleButton, \
    Guna2ControlBox, Guna2GradientButton, \
    Guna2TrackBar, Guna2CheckBox, \
    Guna2CustomCheckBox, Guna2TextBox, \
    Guna2MessageDialog, MessageDialogStyle, \
    MessageDialogIcon, GunaUI_LicenseMgr, \
    Guna2DateTimePicker, Guna2DragControl, \
    Guna2NumericUpDown

from System.Drawing import Color
from System.Windows.Forms import Form
from tkforms import Widget



__all__ = [
    "DEFAULT",
    "TOGGLE"
    "MATERIAL",
    "LIGHT",
    "DARK",
    "ERROR",
    "QUESTION",
    "WARNING",
    "INFORMATION",
    "Button",
    "CheckBox",
    "Chip",
    "CircleButton",
    "ComboBox",
    "ControlBox",
    "CustomCheckBox",
    "DateTimePicker",
    "GradientButton",
    "GunaBase",
    "LicenseDialog",
    "MessageDialog",
    "SpinBox",
    "TextBox",
    "TrackBar",
]


class DragControl:
    def __init__(self, target: Widget = None):
        self._init_widget()
        self.configure(target=target)

    def _init_widget(self):
        self._widget = Guna2DragControl()

    def configure(self, target: Widget = None):
        if target is not None:
            self._widget.TargetControl = target.widget()

    config = configure





class SpinBox(GunaBase):
    def _init_widget(self):
        self._widget = Guna2NumericUpDown()


if __name__ == '__main__':
    from tkinter import Tk, font, Frame
    from tkforms.toolbar import ToolBar
    root = Tk()
    from tkinter import Wm
    root.configure(background="#1d262c")
    root.geometry("250x360")

    btn1 = Button()
    btn1.configure(text="Hello", background=(255, 32, 164, 255), foreground=(255, 32, 164, 255))
    btn1.pack(fill="x")

    btn2 = Button()
    btn2.configure(background=(255, 137, 13, 255))
    btn2.pack(fill="x")

    root.mainloop()