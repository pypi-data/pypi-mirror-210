import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import DockStyle, AnchorStyles, ToolStripGripStyle, ToolStripRenderMode, Padding, \
    ToolStrip, ToolStripButton, ToolStripItem
from System.Drawing import Point, Size, Image, Color
from tkinter import Frame

def tk_forms(parent, child):  # 将Winform组件添加入Tkinter组件
    from ctypes import windll
    windll.user32.SetParent(int(str(child.Handle)), windll.user32.GetParent(parent.winfo_id()))  # 调用win32设置winform组件的父组件


class ToolBar(Frame):
    def __init__(self, *args, side="top", width=25, tooltip="", **kwargs):
        super().__init__(*args, **kwargs)
        self._toolbar = ToolStrip()  # 创建ToolStrip工具栏类
        self._toolbar.Location = Point(0, 0)  # 设置工具栏的位置
        self._width = width  # 设置工具栏的宽度
        self._toolbar.ToolTipText = tooltip  # 设置工具栏的工具提示
        if side == "top":
            _dock = DockStyle.Top
        elif side == "bottom":
            _dock = DockStyle.Bottom
        elif side == "left":
            _dock = DockStyle.Left
        elif side == "right":
            _dock = DockStyle.Right
        self._toolbar.Dock = _dock  # 设置工具栏靠边的方向
        self._toolbar.Anchor = (AnchorStyles.Left | AnchorStyles.Top)  # 设置工具栏布局锚点
        tk_forms(self, self._toolbar)  # 将工具栏嵌入容器
        self.visible(False)  # 默认将工具栏不显示
        self.bind("<Configure>", self._evt_configure)  # 因为WinForm组件无法完美嵌入窗口布局，只能使用自动调整

    def _evt_configure(self, _=None):
        from tkinter import _default_root
        self._toolbar.Location = Point(self.winfo_x(), self.winfo_y())
        if self.side() == "top" or self.side() == "bottom":
            self._toolbar.Size = Size(self.winfo_width(), self._width)
        if self.side() == "left" or self.side() == "right":
            self._toolbar.Size = Size(self._width, self.winfo_height())

    def background(self, alpha=255, red=255, green=255, blue=255):
        self._toolbar.BackColor = Color.FromArgb(alpha, red, green, blue)

    def width(self, width: int = None):
        if width is None:
            return self._width
        else:
            self._width = width

    def side(self, side: str = None):
        if side is None:
            if self._toolbar.Dock == DockStyle.Top:
                return "top"
            elif self._toolbar.Dock == DockStyle.Bottom:
                return "bottom"
            elif self._toolbar.Dock == DockStyle.Left:
                return "left"
            elif self._toolbar.Dock == DockStyle.Right:
                return "right"
        else:
            if side == "top":
                _dock = DockStyle.Top
            elif side == "bottom":
                _dock = DockStyle.Bottom
            elif side == "left":
                _dock = DockStyle.Left
            elif side == "right":
                _dock = DockStyle.Right
            self._toolbar.Dock = _dock

    def visible(self, boolean):
        self._toolbar.Visible = boolean

    def grip(self, visible: bool = None):
        if visible is None:
            return self._toolbar.GripStyle
        else:
            if visible:
                _visible = ToolStripGripStyle.Visible
            else:
                _visible = ToolStripGripStyle.Hidden
            self._toolbar.GripStyle = _visible

    def girp_margin(self, margin):
        if type(margin).__name__ == "list":
            self._toolbar.GripMargin = Padding(margin[0], margin[1], margin[2], margin[3])
        else:
            self._toolbar.GripMargin = Padding(margin)

    def create_button(self, text=None, image=None, on_click=None):
        button = ToolStripButton()
        if text is not None:
            button.Text = text
        if image is not None:
            button.Image = Image.FromFile(image)
        if on_click is not None:
            def click(e1):
                events = {
                    "text": e1.Text
                }
                on_click(events)

            button.Click += lambda e1, e2: click(e1)

        self._toolbar.Items.AddRange({button})
        return button

    def system(self, style=False):
        if style:
            self._toolbar.RenderMode = ToolStripRenderMode.System
        else:
            self._toolbar.RenderMode = ToolStripRenderMode.Professional

    def show(self):
        self.visible(True)
        if self.side() == "top":
            self.pack(side="top", fill="x", ipady=self._width / 2 - 1)
        elif self.side() == "bottom":
            self.pack(side="bottom", fill="x", ipady=self._width / 2 - 1)
        elif self.side() == "left":
            self.pack(side="left", fill="y", ipadx=self._width / 2 - 1)
        elif self.side() == "right":
            self.pack(side="right", fill="y", ipadx=self._width / 2 - 1)


if __name__ == '__main__':
    from tkinter import Tk, Frame, Button

    def e1(_1, _2):
        print(_1)
        print(_2)

    root = Tk()
    toolbar = ToolBar()
    toolbar.create_button("HelloWorld")
    toolbar.show()
    root.mainloop()
