from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroText(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroTextBox
        self._widget = MetroTextBox()

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