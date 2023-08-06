class FlyMetroToolTip(object):
    def __init__(self):
        self.init()

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Components import MetroToolTip
        self._widget = MetroToolTip()

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "theme" in kwargs:
            from MetroFramework import MetroThemeStyle
            style = kwargs.pop("theme")
            if style == "light":
                self._widget.Theme = MetroThemeStyle.Light
            elif style == "dark":
                self._widget.Theme = MetroThemeStyle.Dark
        elif "style" in kwargs:
            from MetroFramework import MetroColorStyle
            style = kwargs.pop("style")
            if style == "default":
                self._widget.Style = MetroColorStyle.Default
            elif style == "black":
                self._widget.Style = MetroColorStyle.Black
            elif style == "white":
                self._widget.Style = MetroColorStyle.White
            elif style == "silver":
                self._widget.Style = MetroColorStyle.Silver
            elif style == "blue":
                self._widget.Style = MetroColorStyle.Blue
            elif style == "green":
                self._widget.Style = MetroColorStyle.Green
            elif style == "lime":
                self._widget.Style = MetroColorStyle.Lime
            elif style == "teal":
                self._widget.Style = MetroColorStyle.Teal
            elif style == "orange":
                self._widget.Style = MetroColorStyle.Orange
            elif style == "brown":
                self._widget.Style = MetroColorStyle.Brown

    def cget(self, attribute_name: str) -> any:
        from MetroFramework import MetroThemeStyle
        if attribute_name == "theme":
            style = self._widget.Theme
            if style == MetroThemeStyle.Light:
                return "light"
            elif style == MetroThemeStyle.Dark:
                return "dark"

    def set_tooltip(self, widget, message: str):
        self._widget.SetToolTip(widget.widget(), message)