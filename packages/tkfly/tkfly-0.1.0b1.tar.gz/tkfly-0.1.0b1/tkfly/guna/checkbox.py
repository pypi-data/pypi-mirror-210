from tkfly.guna.button import FlyGunaButton


class FlyGunaCheckBox(FlyGunaButton):
    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2CheckBox
        self._widget = Guna2CheckBox()

        def changed(*args, **kwargs):
            self.event_generate("<<CheckedChanged>>")

        self._widget.CheckedChanged += changed

    def configure(self, **kwargs):
        if "checked" in kwargs:
            self._widget.Checked = kwargs.pop("checked")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "checked":
            return self._widget.Checked
        else:
            return super().cget(attribute_name)