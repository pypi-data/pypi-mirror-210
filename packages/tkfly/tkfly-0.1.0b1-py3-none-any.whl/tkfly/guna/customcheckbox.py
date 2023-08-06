from tkfly.guna.checkbox import FlyGunaCheckBox


class FlyGunaCustomCheckBox(FlyGunaCheckBox):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2CustomCheckBox
        self._widget = Guna2CustomCheckBox()
