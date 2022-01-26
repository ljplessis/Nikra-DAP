



#TODO Include license




import FreeCAD
from FreeCAD import Units
import os
import os.path
import numpy 
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapForceSelection
import _BodySelector 
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapForce:
    """ Taskpanel for adding DAP Force """
    

    def __init__(self, obj):
        self.obj = obj
        self.Type = self.obj.ForceTypes

        self.X = self.obj.gx
        self.Y = self.obj.gy
        self.Z = self.obj.gz

        self.Stiff=self.obj.Stiffness
        self.UndefLen=self.obj.UndeformedLength


        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2

        self.doc_name = self.obj.Document.Name

        self.default_stiffness = "1 kg/s^2"  
        self.default_length = "1 mm"
        self.default_acceleration = "1 m/s^2"

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapForces.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)


        self.form.forceComboBox.addItems(DapForceSelection.FORCE_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapForceSelection.FORCE_TYPES, self.Type, 0)
        self.form.forceComboBox.setCurrentIndex(bi)

        self.bodySelector = _BodySelector.BodySelector(self.form.bodySelection, self.obj)

        self.form.forceComboBox.currentIndexChanged.connect(self.comboTypeChanged)

        self.comboTypeChanged()

        self.unitFunc()

        self.rebuildInputs()
    
        return 

    def bodySelectionPage(self):
        if self.Type == "Spring":
            self.bodySelector.Page1()
        else: 
            self.bodySelector.closing()
    
    def unitFunc(self):

        acceleration = Units.Quantity(self.default_acceleration)
        length = Units.Quantity(self.default_length)
        stiffness = Units.Quantity(self.default_stiffness)

        setQuantity(self.form.xIn,acceleration)
        setQuantity(self.form.yIn,acceleration)
        setQuantity(self.form.zIn,acceleration)
        setQuantity(self.form.undefIn,length)
        setQuantity(self.form.stiffnessIn,stiffness)

        return 

    def rebuildInputs(self):
    
        setQuantity(self.form.xIn, self.X)
        setQuantity(self.form.yIn, self.Y)
        setQuantity(self.form.zIn, self.Z)
        setQuantity(self.form.stiffnessIn, self.Stiff)
        setQuantity(self.form.undefIn, self.UndefLen)

        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2
    
    
    def accept(self):
        """If this is missing, there won't be an OK button"""
        
        if DapTools.gravityChecker():
            FreeCAD.Console.PrintError('Gravity has already been selected')
        else:
            if self.Type == "Gravity":
                self.bodySelector.closing()
            elif self.Type == "Spring":
                 self.bodySelector.accept(0)
                 self.bodySelector.closing()

            self.obj.ForceTypes = self.Type
            self.obj.gx = getQuantity(self.form.xIn)
            self.obj.gy = getQuantity(self.form.yIn)
            self.obj.gz = getQuantity(self.form.zIn)
            self.obj.Stiffness = getQuantity(self.form.stiffnessIn)
            self.obj.UndeformedLength = getQuantity(self.form.undefIn)

            self.X=self.obj.gx
            self.Y=self.obj.gy
            self.Z=self.obj.gz
            self.Stiff=self.obj.Stiffness
            self.UndefLen=self.obj.UndeformedLength

        self.bodySelector.execute(self.obj,0)

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)        
        self.bodySelector.reject()
        self.bodySelector.closing()
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True
    

    def comboTypeChanged(self):
        type_index = self.form.forceComboBox.currentIndex()
        self.form.descriptionhelp.setText(DapForceSelection.FORCE_TYPE_HELPER_TEXT[type_index])
        self.Type = DapForceSelection.FORCE_TYPES[type_index]

        self.form.inputForceWidget.setCurrentIndex(type_index)
        self.bodySelectionPage()
        self.obj.recompute()

        if self.Type == "Gravity":
                self.obj.setEditorMode("Stiffness", 2)
                self.obj.setEditorMode("UndeformedLength", 2)
                self.obj.setEditorMode("Body1", 2)
                self.obj.setEditorMode("Body2", 2)
                self.obj.setEditorMode("Joint1", 2)
                self.obj.setEditorMode("Joint2", 2)
                self.obj.setEditorMode("JointCoord1", 2)
                self.obj.setEditorMode("JointCoord2", 2)
                self.obj.setEditorMode("gx", 0)
                self.obj.setEditorMode("gy", 0)
                self.obj.setEditorMode("gz", 0)

        elif self.Type == "Spring":
                self.obj.setEditorMode("gx", 2)
                self.obj.setEditorMode("gy", 2)
                self.obj.setEditorMode("gz", 2)
                self.obj.setEditorMode("Stiffness", 0)
                self.obj.setEditorMode("UndeformedLength", 0)
                self.obj.setEditorMode("Body1", 0)
                self.obj.setEditorMode("Body2", 0)
                self.obj.setEditorMode("Joint1", 0)
                self.obj.setEditorMode("Joint2", 0)
                self.obj.setEditorMode("JointCoord1", 0)
                self.obj.setEditorMode("JointCoord2", 0)
        