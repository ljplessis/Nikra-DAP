



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

        # self.form.pushAdd.clicked.connect(self.buttonAddForceClicked)

        # self.form.pushRemove.clicked.connect(self.buttonRemoveForceClicked)

        # self.form.forceList.currentRowChanged.connect(self.forceListRowChanged)

        self.form.forceComboBox.currentIndexChanged.connect(self.comboTypeChanged)

        self.comboTypeChanged()

        self.unitFunc()

        self.rebuildInputs()

        return 

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
       
  

    # def forceListRowChanged(self, row):
    #     """ Actively select the forces to make it visible when viewing forces already in list """
    #     if len(self.FORCE_TYPES)>0:
    #         item = self.FORCE_TYPES[row]
    #         docName = str(self.doc_name)
    #         doc = FreeCAD.getDocument(docName)

    #         selection_object = doc.getObjectsByLabel(item)[0]
    #         FreeCADGui.Selection.clearSelection()
    #         FreeCADGui.Selection.addSelection(selection_object)
    
    
    def accept(self):
        """If this is missing, there won't be an OK button"""
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        if DapTools.gravityChecker():
            FreeCAD.Console.PrintError('Gravity has already been selected')
        else:
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
            # self.obj.Body1, self.obj.Body2, self.obj.Joint1,self.obj.Joint2 = _BodySelector.BodySelector.accept(self)

            self.bodySelector.accept()
            
        self.bodySelector.closing()


        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        self.bodySelector.closing()
        return True
    

    def comboTypeChanged(self):
        type_index = self.form.forceComboBox.currentIndex()
        self.form.descriptionhelp.setText(DapForceSelection.FORCE_TYPE_HELPER_TEXT[type_index])
        self.Type = DapForceSelection.FORCE_TYPES[type_index]

        self.form.inputWidget.setCurrentIndex(type_index)

        
        if self.Type == "Gravity":
                self.obj.setEditorMode("Stiffness", 2)
                self.obj.setEditorMode("UndeformedLength", 2)
                self.obj.setEditorMode("Body1", 2)
                self.obj.setEditorMode("Body2", 2)
                self.obj.setEditorMode("Joint1", 2)
                self.obj.setEditorMode("Joint2", 2)
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
        
    # def buttonAddForceClicked(self):
    #     sel = FreeCADGui.Selection.getSelection()

    #     for item in sel:
    #         #check to see if part is not of Type DapForce
    #         if hasattr(item,"Proxy"):
    #             if item.Proxy.Type == 'DapForce':
    #                 DapForceFound = True
    #         else:
    #             DapForceFound = False
    #         if hasattr(item, "Shape") and (not DapForceFound):
    #             label = item.Label
    #             if label not in self.forceList:
    #                 self.forceList.append(label)
    #         else:
    #             FreeCAD.Console.PrintError("Selected force has not been selected properly \n")

    #     self.rebuildforceList()
    #     return

    # def buttonRemoveForceClicked(self):
    #     if not self.forceList:
    #         FreeCAD.Console.PrintMessage("Here 1")
    #         return
    #     if not self.form.forceList.currentItem():
    #         FreeCAD.Console.PrintMessage("Here 2")
    #         return
    #     row = self.form.forceList.currentRow()
    #     self.forceList.pop(row)
    #     self.rebuildforceList()


    # def rebuildforceList(self):
    #     self.form.forceList.clear()
    #     for i in range(len(self.forceList)):
    #         self.form.forceList.addItem(self.forceList[i])