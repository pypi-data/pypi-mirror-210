from tkfly.telerik import FlyRadButton, FlyRadFrame
import tkinter as tk


class FlyRadPopupFrame(FlyRadFrame):
    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadPopupContainer
        self._widget = RadPopupContainer()
        self._widget.Visible = False


class FlyRadPopupButton(FlyRadButton):
    def __init__(self, *args, width=100, height=30, text: str = "", tooltip: str = "", theme: str = "", command=None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme, tooltip=tooltip)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadPopupEditor
        self._widget = RadPopupEditor()

    def configure(self, **kwargs):
        if "frame" in kwargs:
            self._widget.AssociatedControl = kwargs.pop("frame").widget()
        super().configure(**kwargs)


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyRadPopupButton()
    frame = FlyRadPopupFrame()
    button2 = FlyRadButton(frame.frame())
    button2.pack()
    button.configure(frame=frame)
    button.pack()
    root.mainloop()