from tkfly.core import *

from tkfly.tklib.tooltip import Tooltip as FlyToolTip
from tkfly.tklib.history import History as FlyHistory
from tkfly.tklib.datefield import DateField as FlyDateField

from tkfly.tkscrollutil import ScrollArea as FlyScrollArea
from tkfly.tkscrollutil import ttkScrollArea as FlyTScrollArea
from tkfly.tkscrollutil import ScrollSync as FlyScrollSync
from tkfly.tkscrollutil import ttkScrollSync as FlyTScrollSync
from tkfly.tkscrollutil import ttkScrolledNoteBook as FlyTScrolledNoteBook
from tkfly.tkscrollutil import addclosetab as FlyAddCloseTab
from tkfly.tkscrollutil import removeclosetab as FlyRemoveCloseTab

from tkfly.blend2d import Blend2D as Fly2D

from tkfly.mkwidgets.calendar import Calendar as FlyMkCalendar
from tkfly.mkwidgets.document import Document as FlyMkDocument
from tkfly.mkwidgets.toolbar import Toolbar as FlyMkToolBar
from tkfly.mkwidgets.window import Window as FlyMkWindow

from tkfly.winico import FlyWinico

from tkfly.ttree import Tree as FlyTTreeView

try:
    import clr
except:
    pass
else:
    from tkfly.metro import *

    from tkfly.guna import *

FlyIsLoadTelerik = False

try:
    import clr
except:
    FlyIsLoadTelerik = False
else:
    import sys
    if sys.platform == "win32":
        import tkfly.telerik as FlyRad
        from tkfly.toolbar import ToolBar as FlyWFToolBar

        FlyIsLoadTelerik = True

