from tkfly.guna.button import FlyGunaButton


class FlyGunaGradientButton(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2GradientButton
        self._widget = Guna2GradientButton()