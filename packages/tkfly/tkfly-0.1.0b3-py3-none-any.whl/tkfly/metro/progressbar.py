from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroProgressBar(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroProgressBar
        self._widget = MetroProgressBar()

    def step(self):
        self._widget.PerformStep()

    def configure(self, **kwargs):
        if "value" in kwargs:
            self._widget.Value = kwargs.pop("value")
        elif "maximum" in kwargs:
            self._widget.Maximum = kwargs.pop("maximum")
        elif "minimum" in kwargs:
            self._widget.Minimum = kwargs.pop("minimum")
        elif "step" in kwargs:
            self._widget.Step = kwargs.pop("step")
        elif "animation" in kwargs:
            self._widget.MarqueeAnimationSpeed = kwargs.pop("animation")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value
        elif attribute_name == "maximum":
            return self._widget.Maximum
        elif attribute_name == "minimum":
            return self._widget.Minimum
        elif attribute_name == "step":
            return self._widget.Step
        elif attribute_name == "animation":
            return self._widget.MarqueeAnimationSpeed
        else:
            return super().cget(attribute_name)