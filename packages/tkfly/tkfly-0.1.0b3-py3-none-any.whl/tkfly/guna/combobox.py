from tkfly.guna._winforms import FlyGunaWidget


class FlyGunaComboBox(FlyGunaWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.text = text

    def init(self):
        from tkfly.guna.load import load
        load()
        from Guna.UI2.WinForms import Guna2ComboBox
        self._widget = Guna2ComboBox()

    def configure(self, **kwargs):
        if "item_height" in kwargs:
            self._widget.ItemHeight = kwargs.pop("item_height")
        elif "text" in kwargs:
            self._widget.PromptText = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "item_height":
            return self._widget.ItemHeight
        elif attribute_name == "text":
            return self._widget.PromptText
        else:
            return super().cget(attribute_name)

    def add(self, item: str):
        self._widget.Items.Add(item)

    def add_items(self, items: tuple):
        self._widget.Items.AddRange(items)

    def clear(self):
        self._widget.Items.Clear()

    def insert(self, index: int, item: str):
        self._widget.Items.Insert(index, item)

    def remove(self, item: str):
        self._widget.Items.Remove(item)

    def remove_at(self, index: int):
        self._widget.Items.RemoveAt(index)

    def count(self):
        return self._widget.Items.Count

    def index(self, item: str):
        return self._widget.Items.IndexOf(item)