from tkfly.guna.button import FlyGunaButton


class FlyGunaChip(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2Chip
        self._widget = Guna2Chip()
