



#TODO Include license



import FreeCAD
import os
import os.path
import DapTools
from DapTools import indexOrDefault
import DapBodySelection
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout


class TaskPanelDapBody:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, obj):
        self.obj = obj
        self.References = self.obj.References
        self.BodyType = self.obj.BodyType
        self.doc_name = self.obj.Document.Name


        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapBodies.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.comboBodyType.addItems(DapBodySelection.BODY_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapBodySelection.BODY_TYPES, self.obj.BodyType, 0)
        self.form.comboBodyType.setCurrentIndex(bi)

        self.form.buttonRemovePart.clicked.connect(self.buttonRemovePartClicked)
        
        self.form.partList.currentRowChanged.connect(self.partListRowChanged)

        self.form.comboBodyType.currentIndexChanged.connect(self.comboTypeChanged)

        self.comboTypeChanged()

        self.form.buttonAddPart.clicked.connect(self.buttonAddPartClicked)

        self.rebuildReferenceList()


    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.References = self.References
        self.obj.BodyType = self.BodyType
        return

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True


    def comboTypeChanged(self):
        type_index = self.form.comboBodyType.currentIndex()
        self.form.labelBodyDescription.setText(DapBodySelection.BODY_TYPE_HELPER_TEXT[type_index])
        self.BodyType = DapBodySelection.BODY_TYPES[type_index]
        
    def buttonAddPartClicked(self):
        sel = FreeCADGui.Selection.getSelection()

        for item in sel:
            #check to see if part is not of Type DapBody
            if hasattr(item,"Proxy"):
                if item.Proxy.Type == 'DapBody':
                    DapBodyFound = True
                    FreeCADGui.Console.PrintMessage("Attempted to add a DapBody to parts list")
            else:
                DapBodyFound = False
            if hasattr(item, "Shape") and (not DapBodyFound):
                label = item.Label
                if label not in self.References:
                    self.References.append(label)
            else:
                FreeCAD.Console.PrintError("Selected object does not have a shape \n")

        self.rebuildReferenceList()
        return

    def buttonRemovePartClicked(self):
        if not self.References:
            FreeCAD.Console.PrintMessage("Here 1")
            return
        if not self.form.partList.currentItem():
            FreeCAD.Console.PrintMessage("Here 2")
            return
        row = self.form.partList.currentRow()
        self.References.pop(row)
        self.rebuildReferenceList()

    def rebuildReferenceList(self):
        self.form.partList.clear()
        for i in range(len(self.References)):
            self.form.partList.addItem(self.References[i])

    def partListRowChanged(self, row):
        """ Actively select the part to make it visible when viewing parts already in list """
        if len(self.References)>0:
            item = self.References[row]
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(item)[0]
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(selection_object)
