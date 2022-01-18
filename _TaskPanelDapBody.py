



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
        self.initHorizontal = self.obj.InitialHorizontal
        self.initVertical = self.obj.InitialVertical
        self.initAngular = self.obj.InitialAngular

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapBodies.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.comboBodyType.addItems(DapBodySelection.BODY_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapBodySelection.BODY_TYPES, self.obj.BodyType, 0)
        self.form.comboBodyType.setCurrentIndex(bi)

        self.bodyType()

        self.form.buttonRemovePart.clicked.connect(self.buttonRemovePartClicked)
        
        self.form.partList.currentRowChanged.connect(self.partListRowChanged)

        self.form.comboBodyType.currentIndexChanged.connect(self.comboTypeChanged)

        self.form.comboBodyType.currentIndexChanged.connect(self.bodyType)

        self.comboTypeChanged()

        self.form.buttonAddPart.clicked.connect(self.buttonAddPartClicked)

        self.form.pbResetInitialConditions.clicked.connect(self.resetInitialConditionsValues)

        self.rebuildReferenceList()

        self.rebuildInitialConditions()


    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.References = self.References
        self.obj.BodyType = self.BodyType
        self.obj.InitialHorizontal = self.form.dsbVelocityHorizontal.value()
        self.obj.InitialVertical = self.form.dsbVelocityVertical.value()
        self.obj.InitialAngular = self.form.dsbVelocityAngular.value()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()

        #Determine if a single body has been referenced under multiple DapBody containers
        self.lstMultiple = DapTools.getListOfBodyReferences()
        self.lstMultiple_set = set(self.lstMultiple)
        self.duplicateReferences = len(self.lstMultiple) != len(self.lstMultiple_set)
        if self.duplicateReferences == True:
            FreeCAD.Console.PrintWarning("\n The following elements have been defined under more than one DapBody:  \n")
            self.lstDuplicates = []
            self.viewed = set()
            for j in self.lstMultiple:
                if j in self.viewed:
                    self.lstDuplicates.append(j)
                else:
                    self.viewed.add(j)
            #Provide the user with a list of objects that have been defined multiple times
            FreeCAD.Console.PrintError(set(self.lstDuplicates))
            FreeCAD.Console.PrintWarning("\n Check for redundant element definitions \n")
        else:
            FreeCAD.Console.PrintMessage("\n All DapBody definitions are uniquely defined \n")
        return #self.obj.InitialHorizontal, self.obj.InitialVertical, self.obj.InitialAngular

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def comboTypeChanged(self):
        type_index = self.form.comboBodyType.currentIndex()
        self.form.labelBodyDescription.setText(DapBodySelection.BODY_TYPE_HELPER_TEXT[type_index])
        self.BodyType = DapBodySelection.BODY_TYPES[type_index]
        self.rebuildInitialConditions()
        
    def buttonAddPartClicked(self):
        sel = FreeCADGui.Selection.getSelection()

        for item in sel:
            #check to see if part is not of Type DapBody
            if hasattr(item,"Proxy"):
                if item.Proxy.Type == 'DapBody':
                    DapBodyFound = True
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
        self.rebuildInitialConditions() #Mod

    def rebuildReferenceList(self):
        self.form.partList.clear()
        for i in range(len(self.References)):
            self.form.partList.addItem(self.References[i])


    def rebuildInitialConditions(self):
        self.form.dsbVelocityHorizontal.setValue(self.initHorizontal)
        self.form.dsbVelocityVertical.setValue(self.initVertical)
        self.form.dsbVelocityAngular.setValue(self.initAngular)

    def partListRowChanged(self, row):
        """ Actively select the part to make it visible when viewing parts already in list """
        if len(self.References)>0:
            item = self.References[row]
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(item)[0]
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(selection_object)

    def bodyType(self):
        if self.form.comboBodyType.currentIndex() == 0:
            self.form.lblInitialConditions.setHidden(True)
            self.form.labelInitConditionDescription.setHidden(True)

            self.form.lblVelocityHorizontal.setHidden(True)
            self.form.lblVelocityVertical.setHidden(True)
            self.form.lblVelocityAngular.setHidden(True)

            self.form.dsbVelocityHorizontal.setHidden(True)
            self.form.dsbVelocityVertical.setHidden(True)
            self.form.dsbVelocityAngular.setHidden(True)

            self.form.pbResetInitialConditions.setHidden(True)

            self.form.dsbVelocityAngular.setValue(0.0)
            self.form.dsbVelocityHorizontal.setValue(0.0)
            self.form.dsbVelocityVertical.setValue(0.0)

            self.initHorizontal = self.form.dsbVelocityHorizontal.value()
            self.initVertical = self.form.dsbVelocityVertical.value()
            self.initAngular = self.form.dsbVelocityAngular.value()

        else:
            self.form.lblInitialConditions.setHidden(False)
            self.form.labelInitConditionDescription.setHidden(False)

            self.form.lblVelocityHorizontal.setHidden(False)
            self.form.lblVelocityVertical.setHidden(False)
            self.form.lblVelocityAngular.setHidden(False)

            self.form.dsbVelocityHorizontal.setHidden(False)
            self.form.dsbVelocityVertical.setHidden(False)
            self.form.dsbVelocityAngular.setHidden(False)

            self.form.pbResetInitialConditions.setHidden(False)

    def resetInitialConditionsValues(self):
        """ Resets the body's initial conditions to zero if the reset button is pushed"""
        self.form.dsbVelocityHorizontal.setValue(0.00)
        self.form.dsbVelocityVertical.setValue(0.00)
        self.form.dsbVelocityAngular.setValue(0.00)
