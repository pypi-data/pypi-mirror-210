from tkfly import fly_local, fly_chdir, fly_root, fly_load5


def _load_tkimg():
    with fly_chdir(fly_local()+"\\tkimg"):
        fly_root().eval("set dir [file dirname [info script]]")
        fly_root().eval(f"source pkgIndex.tcl")
        fly_root().eval("package require Img")


if __name__ == '__main__':
    from tkinter import *

    root = Tk()
    _load_tkimg()
    root.mainloop()
