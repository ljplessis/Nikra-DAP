

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
        self.JointType = self.obj.JointType
        self.JointDefinitionMode = self.obj.JointDefinitionMode
        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2
        self.DisplayCoordinate = self.obj.DisplayCoordinate

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapJoints.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.jointType.addItems(DapJointSelection.JOINT_TYPES)
        ji = indexOrDefault(DapJointSelection.JOINT_TYPES, self.obj.JointType, 0)
        self.form.jointType.currentIndexChanged.connect(self.jointTypeChanged)
        self.form.jointType.setCurrentIndex(ji)
        self.jointTypeChanged()

        dmi = indexOrDefault(DapJointSelection.DEFINITION_MODES[ji], self.obj.JointDefinitionMode, 0)
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
        
        self.form.LCSBody2.addItems(self.body_labels)
        b2i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.LCSBody2.setCurrentIndex(b2i)

        self.form.LCSBody1.currentIndexChanged.connect(self.selectedBody1)
        self.form.LCSBody2.currentIndexChanged.connect(self.selectedBody2)
        #FreeCAD.Console.PrintMessage(body_labels)

        self.form.chooseCoordinateButton.clicked.connect(self.addLCS)


    def accept(self):        
        self.obj.JointType = self.JointType
        self.obj.JointDefinitionMode = self.JointDefinitionMode
        self.obj.Body1 = self.Body1
        self.obj.Body2 = self.Body2
        self.obj.Joint1 = self.Joint1
        self.obj.Joint2 = self.Joint2
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        self.obj.DisplayCoordinate = self.DisplayCoordinate
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def jointTypeChanged(self):
        index =  self.form.jointType.currentIndex()
        self.form.definitionMode.clear()
        self.form.definitionMode.addItems(DapJointSelection.DEFINITION_MODES[index])

    def definitionModeChanged(self):
        joint_type_index = self.form.jointType.currentIndex()
        definition_mode_index = self.form.definitionMode.currentIndex()
        self.form.helperText.setText(DapJointSelection.HELPER_TEXT[joint_type_index][definition_mode_index])
        
        self.form.definitionWidget.setCurrentIndex(definition_mode_index)
        
        if definition_mode_index == 0 and self.Joint1 != "":
            self.form.LCSObjectReference.setText(self.Joint1)
        
    def selectedBody1(self):
        index = self.form.LCSBody1.currentIndex()
        self.Body1 = self.body_labels[index]
        self.selectObjectInGui(index)
    
    def selectedBody2(self):
        index = self.form.LCSBody2.currentIndex()
        self.Body2 = self.body_labels[index]
        self.selectObjectInGui(index)
        
    def selectObjectInGui(self, index):
        FreeCADGui.Selection.clearSelection()
        FreeCAD.Console.PrintMessage(self.body_labels[index])
        if self.body_objects[index] != None:
            FreeCADGui.showObject(self.body_objects[index])
            FreeCADGui.Selection.addSelection(self.body_objects[index])

    def addLCS(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        updated = False
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected when defining co-ordinate.")
        else:
            if "LCS" in sel[0].Object.Name:
                self.form.LCSObjectReference.setText(sel[0].Object.Label)
                updated = True
                self.obj.DisplayCoordinate = sel[0].Object.Placement.Base
                self.Joint1 = sel[0].Object.Label
            else:
                sub_element_name = sel[0].SubElementNames[0]
                elt =  sel[0].Object.Shape.getElement(sel[0].SubElementNames[0])
                if elt.ShapeType == "Edge" or elt.ShapeType == "Face":
                    obj_text = sel[0].Object.Name + ":" + sel[0].SubElementNames[0]
                    self.form.LCSObjectReference.setText(obj_text)
                    updated = True
                    self.obj.DisplayCoordinate = elt.CenterOfGravity
                    self.Joint1 = obj_text

        if updated:
            #Recomputing document to add joint type visualisation
            doc_name = str(self.obj.Document.Name)
            FreeCAD.getDocument(doc_name).recompute()
                #if "Face" in sub_element_name or "Edge" in sub_element_name:
                    #return
        #if sel[0].subEleme
        #for item in sel:
            #if hasattr(item, "Shape")
        return
