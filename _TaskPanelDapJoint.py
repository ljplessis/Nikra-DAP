

#TODO Include license



import FreeCAD
import os
import os.path
import DapTools
from DapTools import indexOrDefault
from DapTools import addObjectProperty
import DapJointSelection
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    


class TaskPanelDapJoint:
    """ Taskpanel for adding DAP Joints """
    
    def __init__(self, obj):
        self.obj = obj
        self.TypeOfRelMov = self.obj.TypeOfRelMov
        self.RelMovDefinitionMode = self.obj.RelMovDefinitionMode
        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Point1RelMov = self.obj.Point1RelMov
        self.Point2RelMov = self.obj.Point2RelMov
        self.CoordPoint1RelMov = self.obj.CoordPoint1RelMov
        self.CoordPoint2RelMov = self.obj.CoordPoint2RelMov

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapJoints.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.TypeOfRelMov.addItems(DapJointSelection.JOINT_TYPES)
        ji = indexOrDefault(DapJointSelection.JOINT_TYPES, self.obj.TypeOfRelMov, 0)
        self.form.TypeOfRelMov.currentIndexChanged.connect(self.jointTypeChanged)
        self.form.TypeOfRelMov.setCurrentIndex(ji)
        self.jointTypeChanged()

        dmi = indexOrDefault(DapJointSelection.DEFINITION_MODES[ji], self.obj.RelMovDefinitionMode, 0)
        self.form.definitionMode.currentIndexChanged.connect(self.definitionModeChanged)
        self.form.definitionMode.setCurrentIndex(dmi)
        self.definitionModeChanged()


        #FreeCAD.Console.PrintMessage(self.obj.Group)
        active_analysis = DapTools.getActiveAnalysis()
        self.body_labels = ["Ground"]
        self.body_objects = [None]
        for i in active_analysis.Group:
            if "DapBody" in i.Name:
                self.body_labels.append(i.Label)
                self.body_objects.append(i)

        self.form.LCSBody1.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.LCSBody1.setCurrentIndex(b1i)
        self.selectedBody1()
                
        self.form.LCSBody2.addItems(self.body_labels)
        b2i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.LCSBody2.setCurrentIndex(b2i)
        self.selectedBody2()

        self.form.comboBoxBody1LinMov.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.comboBoxBody1LinMov.setCurrentIndex(b1i)        
        self.selectedBody1()

        self.form.comboBoxBody2LinMov.addItems(self.body_labels)
        b2i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.comboBoxBody2LinMov.setCurrentIndex(b2i)
        self.selectedBody2()        

        self.form.LCSBody1.currentIndexChanged.connect(self.selectedBody1)
        self.form.LCSBody2.currentIndexChanged.connect(self.selectedBody2)
        self.form.comboBoxBody1LinMov.currentIndexChanged.connect(self.selectedBody1)
        self.form.comboBoxBody2LinMov.currentIndexChanged.connect(self.selectedBody2)

        self.form.chooseCoordinateButton.clicked.connect(self.addLCS1)
        self.form.PushButtonLCS1LinMov.clicked.connect(self.addLCS1)
        self.form.PushButtonLCS2LinMov.clicked.connect(self.addLCS2)
      
    def accept(self):        
        self.obj.RelMovDefinitionMode = self.RelMovDefinitionMode
        self.obj.Body1 = self.Body1
        self.obj.Body2 = self.Body2
        if self.obj.Body1 == self.obj.Body2:
            FreeCAD.Console.PrintError("\nERROR: A relative movement has been defined between a body and itself.")
            FreeCAD.Console.PrintError("  Please update the incorrect relative movement so that it is defined between 2 different bodies.")
        
        self.obj.Point1RelMov = self.Point1RelMov
        self.obj.Point2RelMov = self.Point2RelMov
        
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    def reject(self):
        self.obj.TypeOfRelMov = self.TypeOfRelMov
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        self.obj.CoordPoint1RelMov = self.CoordPoint1RelMov
        self.obj.CoordPoint2RelMov = self.CoordPoint2RelMov 
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def jointTypeChanged(self):
        index =  self.form.TypeOfRelMov.currentIndex()
        self.form.definitionMode.clear()
        self.form.definitionMode.addItems(DapJointSelection.DEFINITION_MODES[index])
        self.obj.TypeOfRelMov = DapJointSelection.JOINT_TYPES[index]
        self.obj.recompute()
        
    def definitionModeChanged(self):
        self.joint_type_index = self.form.TypeOfRelMov.currentIndex()
        definition_mode_index = self.form.definitionMode.currentIndex()
        self.RelMovDefinitionMode = DapJointSelection.DEFINITION_MODES[self.joint_type_index][definition_mode_index]
        self.form.helperText.setText(DapJointSelection.HELPER_TEXT[self.joint_type_index][definition_mode_index])
        current_index = self.findDefinitionWidgetIndex(self.joint_type_index, definition_mode_index)
        self.form.definitionWidget.setCurrentIndex(current_index)
        
        if definition_mode_index == 0:
            if self.joint_type_index == 0 and self.Point1RelMov != "":
                self.form.LCSObjectReference.setText(self.Point1RelMov)
            elif self.joint_type_index == 1:
                if self.Point1RelMov != "":
                    self.form.objectNameLCS1LinMov.setText(self.Point1RelMov)
                if self.Point2RelMov != "":
                    self.form.objectNameLCS2LinMov.setText(self.Point2RelMov)

    def findDefinitionWidgetIndex(self, joint_index, definition_index):
        current_count = 0
        if joint_index>0:
            for i in range(joint_index):
                current_count += len(DapJointSelection.DEFINITION_MODES[i])
        current_count += definition_index
        return current_count
        
    def selectedBody1(self):
        if self.joint_type_index == 0:
            index = self.form.LCSBody1.currentIndex()
        elif self.joint_type_index == 1:
            index = self.form.comboBoxBody1LinMov.currentIndex()
        self.Body1 = self.body_labels[index]
        self.selectObjectInGui(index)
    
    def selectedBody2(self):
        if self.joint_type_index == 0:
            index = self.form.LCSBody2.currentIndex()
        elif self.joint_type_index == 1:
            index = self.form.comboBoxBody2LinMov.currentIndex()
        self.Body2 = self.body_labels[index]
        self.selectObjectInGui(index)
        
    def selectObjectInGui(self, index):
        FreeCADGui.Selection.clearSelection()
        if self.body_objects[index] != None:
            FreeCADGui.showObject(self.body_objects[index])
            FreeCADGui.Selection.addSelection(self.body_objects[index])

    def addLCS1(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        updated = False
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected when defining co-ordinate.")
        else:
            if "LCS" in sel[0].Object.Name:
                if self.joint_type_index == 0:
                    self.form.LCSObjectReference.setText(sel[0].Object.Label)
                    self.obj.CoordPoint1RelMov = sel[0].Object.Placement.Base
                    updated = True

                elif self.joint_type_index == 1:
                    self.form.objectNameLCS1LinMov.setText(sel[0].Object.Label)
                    self.obj.CoordPoint1RelMov = sel[0].Object.Placement.Base
                
                self.Point1RelMov = sel[0].Object.Label
                if self.Point2RelMov != "":
                    updated = True
        if updated:
            self.obj.recompute()

    def addLCS2(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected.")
        else:
            if "LCS" in sel[0].Object.Name:
                if self.joint_type_index == 1:
                    self.form.objectNameLCS2LinMov.setText(sel[0].Object.Label)
                    self.obj.CoordPoint2RelMov = sel[0].Object.Placement.Base
                    self.Point2RelMov = sel[0].Object.Label
                    
                    if self.Point1RelMov != "":
                        self.obj.recompute()
