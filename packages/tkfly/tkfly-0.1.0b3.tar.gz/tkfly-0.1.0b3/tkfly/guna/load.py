import os
lib = os.path.dirname(__file__).replace("\\", "//")
gunaui2_lib = lib + "//Guna.UI2.dll"

def load():
    import clr
    clr.AddReference(gunaui2_lib)
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")