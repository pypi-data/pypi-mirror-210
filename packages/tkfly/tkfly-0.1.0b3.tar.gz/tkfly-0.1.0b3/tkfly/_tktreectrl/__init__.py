from tkfly import fly_local, fly_chdir, fly_root, fly_load5


def _load_tktreectrl():
    with fly_chdir(fly_local()+"\\tkimg"):
        fly_root().eval("set dir [file dirname [info script]]")
        fly_root().eval(f"source pkgIndex.tcl")
        fly_root().eval("package require treectrl")


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    _load_tktreectrl()

    root.eval("""
package require treectrl
treectrl .t
pack .t
# create an element, that should hold the text of the cell later:
.t element create el1 text
# create a style to be used for the cells:
.t style create s1
# tell the style s1 that it should consist of the text element e1:
.t style elements s1 el1
# now, add a new column to the table and assign the items of that column (which are added in the next step) the style s1
.t column create -text "My texts" -expand yes -itemstyle s1
# now, we are ready to add the first item (.i.e the first row of the table):
# create a new item as a new child of the always existing root item:
set itm [.t item create -parent root]
# give the item a label:
# (we use a convenience command here that assigns the given text to the first text element found in this cell)
# (Otherwise, the command should be: .t item element configure $itm 0 el1 -text "Hello World")
.t item text $itm 0 "Hello World"
# add another item:
set item [.t item create -parent root]
.t item text $item 0 "And good luck with treectrl"
    """)

    root.mainloop()