



#TODO Include license




import FreeCAD
from FreeCAD import Units
import os
import os.path
import numpy 
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapPointSelection
import _BodySelector 
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapPoint:
    """ Taskpanel for adding DAP Point """
    

    def __init__(self, obj):
        self.obj = obj
        self.Body = self.obj.Body
        self.Point = self.obj.Point 
        self.PointCoord = self.obj.PointCoord 
 
        self.doc_name = self.obj.Document.Name

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapPoint.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.bodySelector = _BodySelector.BodySelector(self.form.bodySelection, self.obj)
        
        self.bodySelectionPage()

        self.rebuildInputs()
        
        return 

    
    def bodySelectionPage(self):
        self.bodySelector.Page3()

    def rebuildInputs(self):
        self.Body = self.obj.Body
        self.Point = self.obj.Point 
        self.PointCoord = self.obj.PointCoord
        

    def accept(self):
        """If this is missing, there won't be an OK button"""
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.Body = self.Body
        self.obj.Point = self.Point 
        self.obj.PointCoord = self.PointCoord

        self.bodySelector.accept(2)
        self.bodySelector.pointExecute(self.obj)
            
        self.bodySelector.closing()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        # self.obj.recompute()
        
        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        self.bodySelector.reject()
        self.bodySelector.closing()
        return True
    

  