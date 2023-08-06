# From https://github.com/m0x3/Python3-Mutliple-Document-Interface/tree/master

try:
    import Pmw
except:
    pass
else:
    from tkmfly.tkmdi.Widgets.MDI import MDIChild as FlyXMDIChild, MDIParent as FlyXMDIParent
    from tkmfly.tkmdi.Widgets.iconPath import path as FlyXMDIIconPath
    from tkmfly.tkmdi.Widgets.FlatButtons import Flatbutton as FlyXFlatButton, FlatRadiobutton as FlyXFlatRadioButton, \
        FlatRadiogroup as FlyXFlatRadioGroup
    from tkmfly.tkmdi.Widgets.Toolbar import Toolbar as FlyXToolBar
    from tkmfly.tkmdi.Widgets.Tree import Tree as FlyXTreeView
    from tkmfly.tkmdi.Widgets.ProgressBar import ProgressBar as FlyXProgressBar