import tkinter as tk


class TreeCtrl(tk.Widget):
    def __init__(self, master=None):
        from tkfly._tktreectrl import _load_tktreectrl
        _load_tktreectrl()
        super().__init__(master, "treectrl")

    def test(self):
        self.tk.eval("""
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

    def column(self, *args):
        """
        This command is used to manipulate the columns of the treectrl widget (see section COLUMNS below). The exact
        behavior of the command depends on the option argument that follows the column argument.
        """
        return self.tk.call(self._w, 'column', *args)

    def column_create(self, text: str = ""):
        return self.column("create", "-text", text)

    def _column_configure(self, columnDesc, attribute_name, attribute_value):
        self.column("configure", columnDesc, attribute_name, attribute_value)

    def column_configure(self, columnDesc, **kwargs):
        if "text" in kwargs:
            self._column_configure(columnDesc, "-text", kwargs.pop("text"))

    def column_cget(self, columnDesc, option):
        return self.column("cget", columnDesc, "-"+option)

    def item(self, *args):
        """
        This command is used to manipulate items. The exact behavior of the command depends on the option argument
        that follows the item argument.
        """
        return self.tk.call(self._w, 'item', *args)

    def item_create(self, parent=0):
        return self.item("create", "-parent", parent)

    def item_text(self, itemDesc, column, text: str = ""):
        return self.item("text", itemDesc, column, text)

    def item_id(self, itemDesc):
        return self.item("id", itemDesc)

    def item_parent(self, itemDesc):
        return self.item("parent", itemDesc)


if __name__ == '__main__':
    root = tk.Tk()

    treectrl = TreeCtrl()
    column1 = treectrl.column_create(text="Hello?")
    column2 = treectrl.column_create(text="Hi?")
    print(treectrl.column_cget(column1, "text"))
    treectrl.column_configure(column2, text="Is there!")
    item1 = treectrl.item_create(column1)
    treectrl.item_text(item1, column1, "hello")
    treectrl.pack()

    root.mainloop()