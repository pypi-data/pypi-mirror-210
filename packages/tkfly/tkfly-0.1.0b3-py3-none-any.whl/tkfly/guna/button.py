from tkfly.guna._winforms import FlyGunaWidget


class FlyGunaButton(FlyGunaWidget):
    def __init__(self, *args, width=100, height=30, text="GunaUI2.Button", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.text = text

    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2Button
        self._widget = Guna2Button()

        def checked(*args, **kwargs):
            self.event_generate("<<CheckedChanged>>")

        self._widget.CheckedChanged += checked

    def configure(self, **kwargs):
        if "mode" in kwargs:
            from Guna.UI2.WinForms.Enums import ButtonMode
            mode = kwargs.pop("mode")
            if mode == "default":
                self._widget.ButtonMode = ButtonMode.DefaultButton
            elif mode == "toggle":
                self._widget.ButtonMode = ButtonMode.ToogleButton
            elif mode == "radio":
                self._widget.ButtonMode = ButtonMode.RadioButton
        if "checked" in kwargs:
            self._widget.Checked = kwargs.pop("checked")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        from Guna.UI2.WinForms.Enums import ButtonMode
        if attribute_name == "checked":
            return self._widget.Checked
        elif attribute_name == "mode":
            mode = self._widget.ButtonMode
            if mode == ButtonMode.DefaultButton:
                return "default"
            elif mode == ButtonMode.ToogleButton:
                return "toggle"
            elif mode == ButtonMode.RadioButton:
                return "radio"
        elif attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)
