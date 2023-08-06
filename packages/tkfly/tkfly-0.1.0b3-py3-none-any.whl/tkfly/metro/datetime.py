from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroDateTime(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        def value_changed(*args, **kwargs):
            self.event_generate("<<ValueChanged>>")

        self._widget.ValueChanged += value_changed

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroDateTime
        self._widget = MetroDateTime()

    def configure(self, **kwargs):
        if "value" in kwargs:
            value = kwargs.pop("value")
            from System import DateTime
            self._widget.Value = DateTime(value[0], value[1], value[2])
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            date = self._widget.Value
            return (date.Year, date.Month, date.Day)
        else:
            return super().cget(attribute_name)