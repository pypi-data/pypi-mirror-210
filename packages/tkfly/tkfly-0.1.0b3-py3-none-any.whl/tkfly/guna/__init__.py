import tkinter as tk

from tkfly.guna._winforms import FlyGunaWidget, FlyGunaFrame

from tkfly.guna.button import FlyGunaButton
from tkfly.guna.checkbox import FlyGunaCheckBox
from tkfly.guna.chip import FlyGunaChip
from tkfly.guna.circlebutton import FlyGunaCircleButton
from tkfly.guna.combobox import FlyGunaComboBox
from tkfly.guna.core import *
from tkfly.guna.customcheckbox import FlyGunaCustomCheckBox
from tkfly.guna.datetimepicker import FlyGunaDateTimePicker
from tkfly.guna.gradientbutton import FlyGunaGradientButton
from tkfly.guna.licensedialog import FlyGunaLicenseDialog
from tkfly.guna.messagebox import FlyGunaMessageDialog
from tkfly.guna.text import FlyGunaText
from tkfly.guna.trackbar import FlyGunaTrackBar
from tkfly.guna.widgetbox import FlyGunWidgetBox

if __name__ == '__main__':
    root = tk.Tk()

    button = FlyGunaButton()
    button.configure(animated=True)
    button.configure(border_radius=12)
    button.pack()

    import Guna.UI2.WinForms
    help(Guna.UI2.WinForms)

    root.mainloop()