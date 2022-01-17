



#TODO Include license




import FreeCAD
import os
import os.path
import numpy 
import DapTools
from DapTools import indexOrDefault
import DapForceSelection
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout


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


        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapForces.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.forceComboBox.addItems(DapForceSelection.FORCE_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapForceSelection.FORCE_TYPES, self.Type, 0)
        self.form.forceComboBox.setCurrentIndex(bi)

        # self.form.pushAdd.clicked.connect(self.buttonAddForceClicked)

        # self.form.pushRemove.clicked.connect(self.buttonRemoveForceClicked)

        # self.form.forceList.currentRowChanged.connect(self.forceListRowChanged)

        self.form.forceComboBox.currentIndexChanged.connect(self.comboTypeChanged)


    

        self.comboTypeChanged()

        self.rebuildInputs()
        


        return 

    def rebuildInputs(self):
        self.form.xIn.insertPlainText(self.X)
        self.form.yIn.insertPlainText(self.Y)
        self.form.zIn.insertPlainText(self.Z)
        self.form.stiffnessIn.insertPlainText(self.Stiff)
        self.form.undefIn.insertPlainText(self.UndefLen)
  

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
            self.obj.gx = self.form.xIn.toPlainText()
            self.obj.gy = self.form.yIn.toPlainText()
            self.obj.gz = self.form.zIn.toPlainText()
            self.obj.Stiffness = self.form.stiffnessIn.toPlainText()
            self.obj.UndeformedLength = self.form.undefIn.toPlainText()
        
        # self.obj.gx = self.X
        # self.obj.gy = self.Y
        # self.obj.gz = self.Z

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