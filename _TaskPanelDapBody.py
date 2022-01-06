



#TODO Include license



import FreeCAD
import os
import os.path
import CfdTools
from CfdTools import getQuantity, setQuantity, indexOrDefault
import CfdFaceSelectWidget
import CfdFluidBoundary
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout


class TaskPanelDapBody:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, obj):
        self.obj = obj



    def accept(self):
        return


    def reject(self):
        return True
