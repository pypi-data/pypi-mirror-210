from tkfly.guna.button import FlyGunaButton


class FlyGunWidgetBox(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2ControlBox
        self._widget = Guna2ControlBox()