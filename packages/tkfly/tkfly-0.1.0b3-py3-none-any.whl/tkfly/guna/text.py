from tkfly.guna._winforms import FlyGunaWidget


class FlyGunaText(FlyGunaWidget):
    def _init_widget(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2TextBox
        self._widget = Guna2TextBox()

        def changed(*args, **kwargs):
            self.event_generate("<<TextChange>>")

        self._widget.TextChanged += changed

    def configure(self, **kwargs):
        if "multiline" in kwargs:
            self._widget.Multiline = kwargs.pop("multiline")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "multiline":
            return self._widget.Multiline
        elif attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)
