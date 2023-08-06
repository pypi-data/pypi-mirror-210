from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroTrackBar(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroTrackBar
        self._widget = MetroTrackBar()

        def changed(*args, **kwargs):
            self.event_generate("<<ValueChanged>>")

        self._widget.ValueChanged += changed

    def configure(self, **kwargs):
        if "value" in kwargs:
            self._widget.Value = kwargs.pop("value")
        elif "maximum" in kwargs:
            self._widget.Maximum = kwargs.pop("maximum")
        elif "minimum" in kwargs:
            self._widget.Minimum = kwargs.pop("minimum")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value
        elif attribute_name == "maximum":
            return self._widget.Maximum
        elif attribute_name == "minimum":
            return self._widget.Minimum
        else:
            return super().cget(attribute_name)