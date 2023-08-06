from tkfly import *
from tkinter import *
from tkinter import ttk


if __name__ == '__main__':
    root = Tk()
    root.title("tkfly demos")

    try:
        from sv_ttk import toggle_theme, use_light_theme, use_dark_theme
    except:
        pass
    else:
        use_light_theme()

    toolbar_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyToolBar"))

    toolbar = FlyWFToolBar(toolbar_panel)
    toolbar.create_button("command1", on_click=lambda e: print(e))
    toolbar.show()

    toolbar_panel.pack(side="top", fill="x", padx=10, pady=10, ipadx=10, ipady=10)

    tooltip_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyToolTip"))

    label = ttk.Label(tooltip_panel, text="Hover me", anchor=CENTER)
    label.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    tooltip = FlyToolTip(root)
    tooltip.tooltip(label, "I`m a tooltip widget")

    tooltip_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    datefield_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyDateField"))

    datefield = FlyDateField(datefield_panel)
    datefield.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    datefield_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    root.mainloop()