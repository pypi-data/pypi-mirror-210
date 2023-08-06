import os
lib = os.path.dirname(__file__).replace("\\", "//")
metro_lib = lib + "//MetroFramework.dll"
metro_design_lib = lib + "//MetroFramework.Design.dll"
metro_fonts_lib = lib + "//MetroFramework.Fonts.dll"

def load():
    import clr
    clr.AddReference(metro_lib)
    clr.AddReference(metro_fonts_lib)
    clr.AddReference(metro_design_lib)
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")