from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadVirtualKeyboard(FlyRadWidget):
    def __init__(self, *args, width=800, height=200, tooltip: str = "", theme: str = "", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme, tooltip=tooltip)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadVirtualKeyboard
        self._widget = RadVirtualKeyboard()


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyRadVirtualKeyboard()
    button.pack()
    root.mainloop()