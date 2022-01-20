# TODO: Add license 

import FreeCAD
import os
import os.path
import DapTools 
from DapTools import indexOrDefault
from DapTools import addObjectProperty
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import QTimer

class BodySelector:
    def __init__(self, parent_widget, obj):
        ui_path = os.path.join(os.path.dirname(__file__), "BodySelector.ui")
        self.parent_widget = parent_widget
        self.form = FreeCADGui.PySideUic.loadUi(ui_path, self.parent_widget)
        self.parent_widget.layout().addWidget(self.form)

        self.obj = obj
        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2
        # self.DisplayCoordinate = self.obj.DisplayCoordinate

        self.doc_name = self.obj.Document.Name
        self.view_object = self.obj.ViewObject

        active_analysis = DapTools.getActiveAnalysis()
        self.body_labels = ["Ground"]
        self.body_objects = [None]
        for i in active_analysis.Group:
            if "DapBody" in i.Name:
                self.body_labels.append(i.Label)
                self.body_objects.append(i)

        self.form.body1Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.body1Combo.setCurrentIndex(b1i)
        self.selectedBody1()

        self.form.body2Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.body2Combo.setCurrentIndex(b1i)
        self.selectedBody2()

        self.form.lcsPush1.clicked.connect(self.addLCS1)
        self.form.lcsPush2.clicked.connect(self.addLCS2)

        self.form.lcsName1.clicked.connect(lambda : self.selectLCSinGui(self.Joint1))
        self.form.lcsName2.clicked.connect(lambda : self.selectLCSinGui(self.Joint2))
        
        
        self.form.body1Combo.currentIndexChanged.connect(self.selectedBody1)
        self.form.body2Combo.currentIndexChanged.connect(self.selectedBody2)

        self.rebuildInputs()
    
    
    
    def rebuildInputs(self):
        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2

        self.form.lcsName1.setText(self.Joint1)
        self.form.lcsName2.setText(self.Joint2)

        return



    def accept(self):        
        self.obj.Body1 = self.Body1
        self.obj.Body2 = self.Body2
        self.obj.Joint1 = self.Joint1
        self.obj.Joint2 = self.Joint2

        # doc = FreeCADGui.getDocument(self.obj.Document)
        # doc.resetEdit()
        # FreeCAD.Console.PrintError(str(self.obj.Body1))
        # FreeCAD.Console.PrintError(self.Body1)
        # FreeCAD.Console.PrintError("F-it")
        return self.obj.Body1, self.obj.Body2, self.obj.Joint1, self.obj.Joint2

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        # self.obj.DisplayCoordinate = self.DisplayCoordinate
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def selectedBody1(self):
        index = self.form.body1Combo.currentIndex()
        self.Body1 = self.body_labels[index]
        self.selectObjectInGui(index)

    def selectedBody2(self):
        index = self.form.body2Combo.currentIndex()
        self.Body2 = self.body_labels[index]
        self.selectObjectInGui(index)

    def selectObjectInGui(self, index):
        FreeCADGui.Selection.clearSelection()
        #FreeCAD.Console.PrintMessage(self.body_labels[index])
        if self.body_objects[index] != None:
            FreeCADGui.showObject(self.body_objects[index])
            FreeCADGui.Selection.addSelection(self.body_objects[index])
    
    def selectLCSinGui(self,joint):
        FreeCADGui.Selection.clearSelection()
        docName = str(self.doc_name)
        doc = FreeCAD.getDocument(docName)
        selection_object = doc.getObjectsByLabel(joint)[0]
        FreeCADGui.showObject(selection_object)
        FreeCADGui.Selection.addSelection(selection_object)

            

    def addLCS1(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        updated = False
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected when defining co-ordinate.")
        else:
            if "LCS" in sel[0].Object.Name:
                self.form.lcsName1.setText(sel[0].Object.Label)
                updated = True
                # self.obj.DisplayCoordinate = sel[0].Object.Placement.Base
                self.Joint1 = sel[0].Object.Label

    def addLCS2(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        updated = False
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected.")
        else:
            if "LCS" in sel[0].Object.Name:
                self.form.lcsName2.setText(sel[0].Object.Label)
                updated = True
                # self.obj.DisplayCoordinate = sel[0].Object.Placement.Base
                self.Joint2 = sel[0].Object.Label
            
    
    def closing(self):
        """ Call this on close to let the widget to its proper cleanup """
        FreeCADGui.Selection.removeObserver(self)















        

