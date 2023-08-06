class FlyGunaMessageDialog:
    def __init__(self, icon=None, text="", theme="default"):
        self.init()
        self.configure(icon=icon, text=text, theme=theme)

    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2MessageDialog, MessageDialogStyle
        self._widget = Guna2MessageDialog()

    def font(self, name: str = "Sego UI", size: int = 9):
        try:
            font = Font(name, size)
        except TypeError:
            pass
        else:
            self._widget.Font = font

    def configure(self, font=None, icon=None, text=None, theme=None):
        if font is not None:
            try:
                from System.Drawing import Font
                font = Font(font[0], font[1])
            except TypeError:
                pass
            else:
                self._widget.Font = font
                self._widget.Font = font
        elif icon is not None:
            from Guna.UI2.WinForms import MessageDialogIcon
            if icon == "error":
                self._widget.Icon = MessageDialogIcon.Error
            elif icon == "question":
                self._widget.Icon = MessageDialogIcon.Question
            elif icon == "warning":
                self._widget.Icon = MessageDialogIcon.Warning
            elif icon == "information":
                self._widget.Icon = MessageDialogIcon.Information
        elif theme is not None:
            from Guna.UI2.WinForms import MessageDialogStyle
            if theme == "default":
                self._widget.Style = MessageDialogStyle.Default
            elif theme == "light":
                self._widget.Style = MessageDialogStyle.Light
            elif theme == "dark":
                self._widget.Style = MessageDialogStyle.Dark
        elif text is not None:
            self._widget.Text = text

    config = configure

    def cget(self, attribute_name):
        if attribute_name == "theme":
            from Guna.UI2.WinForms import MessageDialogStyle
            theme = self._widget.Style
            if theme == MessageDialogStyle.Default:
                return "default"
            elif theme == MessageDialogStyle.Light:
                return "light"
            elif theme == MessageDialogStyle.Dark:
                return "dark"
        elif attribute_name == "text":
            return self._widget.Text

    def widget(self):
        return self._widget

    def show(self):
        self._widget.Show()