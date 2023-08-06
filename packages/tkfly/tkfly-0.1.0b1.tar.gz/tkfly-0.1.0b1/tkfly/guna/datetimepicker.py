from tkfly.guna.button import FlyGunaButton


class FlyGunaDateTimePicker(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2DateTimePicker
        self._widget = Guna2DateTimePicker()
