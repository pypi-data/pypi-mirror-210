from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroToggleBox(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroToggle
        self._widget = MetroToggle()

        def checked_changed(*args, **kwargs):
            self.event_generate("<<CheckedChanged>>")

        def check_state_changed(*args, **kwargs):
            self.event_generate("<<CheckStateChanged>>")

        self._widget.CheckedChanged += checked_changed
        self._widget.CheckStateChanged += check_state_changed