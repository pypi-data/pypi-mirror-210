from tkfly.metro._winforms import FlyMetroWidget


class FlyMetroCheckBox(FlyMetroWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.metro.load import load
        load()
        from MetroFramework.Controls import MetroCheckBox
        self._widget = MetroCheckBox()

        def checked_changed(*args, **kwargs):
            self.event_generate("<<CheckedChanged>>")

        def check_state_changed(*args, **kwargs):
            self.event_generate("<<CheckStateChanged>>")

        self._widget.CheckedChanged += checked_changed
        self._widget.CheckStateChanged += check_state_changed

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "checked" in kwargs:
            self._widget.Checked = kwargs.pop("checked")
        elif "checkstate" in kwargs:
            check_state = kwargs.pop("checkstate")
            from System.Windows.Forms import CheckState
            if check_state == "indeterminate":
                self._widget.CheckState = CheckState.Indeterminate
            elif check_state == "checked":
                self._widget.CheckState = CheckState.Checked
            elif check_state == "unchecked":
                self._widget.CheckState = CheckState.Unchecked
        elif "checkalign" in kwargs:
            from System.Drawing import Point, Size, ContentAlignment
            check_align = kwargs.pop("checkalign")
            if check_align == "left":
                self._widget.CheckAlign = ContentAlignment.MiddleLeft
            elif check_align == "right":
                self._widget.CheckAlign = ContentAlignment.MiddleRight
            elif check_align == "top":
                self._widget.CheckState = ContentAlignment.TopCenter
            elif check_align == "bottom":
                self._widget.CheckState = ContentAlignment.BottomCenter
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        elif attribute_name == "checked":
            return self._widget.Checked
        elif attribute_name == "checkstate":
            from System.Windows.Forms import CheckState
            check_state = self._widget.CheckState
            if check_state == CheckState.Indeterminate:
                return "indeterminate"
            elif check_state == CheckState.Checked:
                return "checked"
            elif check_state == CheckState.Unchecked:
                return "unchecked"
            return
        else:
            return super().cget(attribute_name)
