import tkinter as tk


class FlyMdi():
    def toplevel_to(self, parent: tk.Tk, toplevel: tk.Toplevel):
        from ctypes import windll
        windll.user32.SetParent(windll.user32.GetParent(toplevel.winfo_id()), windll.user32.GetParent(parent.winfo_id()))


def FlyToMdi(parent: tk.Tk, toplevel: tk.Toplevel):
    from tkfly.core import fly_root
    fly_root().after(10, lambda: FlyMdi().toplevel_to(parent, toplevel))


if __name__ == '__main__':
    root = tk.Tk()
    toplevel1 = tk.Toplevel()
    FlyToMdi(root, toplevel1)
    root.mainloop()