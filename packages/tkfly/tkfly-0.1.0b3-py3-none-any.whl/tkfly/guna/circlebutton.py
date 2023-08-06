from tkfly.guna.button import FlyGunaButton


class FlyGunaCircleButton(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2CircleButton
        self._widget = Guna2CircleButton()