from tkmfly.core import *

from tkmfly.notifywindow import NotifyWindow as FlyNotifyWindow
from tkmfly.tooltip import Tooltip as FlyToolTip
from tkmfly.datefield import DateField as FlyDateField
from tkmfly.history import History as FlyHistory
from tkmfly.ttree import Tree as FlySimpleTree

from tkmfly.tkmdi import *
from tkmfly.mdi import FlyMdi, FlyToMdi

from tkmfly.mkwidgets.calendar import Calendar as FlyMkCalendar
from tkmfly.mkwidgets.document import Document as FlyMkDocument
from tkmfly.mkwidgets.toolbar import Toolbar as FlyMkToolBar
from tkmfly.mkwidgets.window import Window as FlyMkWindow

try:
    import clr
    from tkmfly.toolbar import ToolBar
except ModuleNotFoundError:
    FlyToolBar = ToolBar

