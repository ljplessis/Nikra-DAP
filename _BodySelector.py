# TODO: Add license 

import FreeCAD
import os
import os.path
import DapTools 
from DapTools import indexOrDefault
from DapTools import addObjectProperty
import DapForceSelection
import _TaskPanelDapForce
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import QTimer
import Part
import math
from math import degrees,acos
import _FreeCADVectorTools
from _FreeCADVectorTools import dist, normalized, crossproduct,dotproduct, angle, length


TYPES = ["two points and two bodies","One point and two bodies","One Point and associated point" ]

HELPER_TEXT = ["Choose two points (LCS) and two bodies that points are attached to","Choose one point (LCS) and two bodies","Pick one point and the body associated to it" ]

class BodySelector:
    def __init__(self, parent_widget, obj):
        ui_path = os.path.join(os.path.dirname(__file__), "BodySelector.ui")
        self.parent_widget = parent_widget
        self.form = FreeCADGui.PySideUic.loadUi(ui_path, self.parent_widget)
        self.parent_widget.layout().addWidget(self.form)

        addObjectProperty(obj,"JointType",TYPES, "App::PropertyEnumeration", "", "Joint Types")
        
        self.buttonName = None
        self.obj = obj
    
        self.doc_name = self.obj.Document.Name
        self.view_object = self.obj.ViewObject

        active_analysis = DapTools.getActiveAnalysis()
        self.body_labels = ["Ground"]
        self.body_objects = [None]
        for i in active_analysis.Group:
            if "DapBody" in i.Name:
                self.body_labels.append(i.Label)
                self.body_objects.append(i)
    
    # index == 0
    def Page1(self):
        index = 0
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)

        self.form.body1Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.body1Combo.setCurrentIndex(b1i)
        self.selectedBody1(index)

        self.form.body2Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.body2Combo.setCurrentIndex(b1i)
        self.selectedBody2(index)

        self.form.lcsPush1.clicked.connect(lambda: self.addLCS1(index))
        self.form.lcsPush2.clicked.connect(self.addLCS2)
        

        self.form.lcsName1.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint1))
        self.form.lcsName2.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint2))        
        
        self.form.body1Combo.currentIndexChanged.connect(self.selectedBody1)
        self.form.body2Combo.currentIndexChanged.connect(self.selectedBody2)

        self.rebuildInputs(index)
        self.comboTypeChanged()

        return True
    
        
# index == 1
    def Page2(self):
        index = 1
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)

        self.form.body1Combo_2.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.body1Combo_2.setCurrentIndex(b1i)
        self.selectedBody1(index)

        self.form.body2Combo_2.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.body2Combo_2.setCurrentIndex(b1i)
        self.selectedBody2(index)

        self.form.lcsName3.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint1))
        self.form.lcsPush3.clicked.connect(lambda : self.addLCS1(index))

        self.form.body1Combo_2.currentIndexChanged.connect(self.selectedBody1)
        self.form.body2Combo_2.currentIndexChanged.connect(self.selectedBody2)

        self.rebuildInputs(index)

        self.comboTypeChanged()

        return 

    # index == 2
    def Page3(self):
        index = 2
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)

        self.form.bodyPointCombo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body, 0)
        self.form.bodyPointCombo.setCurrentIndex(b1i)
        self.selectedBody1(index)
        
        self.form.pointPush.clicked.connect(self.addPoint)

        self.form.pointName.clicked.connect(self.selectInGui)

        self.form.bodyPointCombo.currentIndexChanged.connect(self.selectedBody1)

        self.rebuildInputs(index)
        
        self.comboTypeChanged()

        return 

   
    
    def PageInit(self,index):
        # self.index = self.form.inputWidget.currentIndex()
        if index == 0:
            self.JType = self.obj.JointType 
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            self.Joint2 = self.obj.Joint2
            self.JointCoord1 = self.obj.JointCoord1
            self.JointCoord2 = self.obj.JointCoord2

        elif index == 1:
            self.JType = self.obj.JointType
            self.Joint1 = self.obj.Joint1
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2

        elif index == 2:
            self.JType = self.obj.JointType
            self.Point = self.obj.Point 
            self.Body = self.obj.Body
            self.PointCoord = self.obj.PointCoord

    def comboTypeChanged(self):
        
        type_index = self.form.inputWidget.currentIndex()
        self.form.labelHelperText.setText(HELPER_TEXT[type_index])
        self.JType = TYPES[type_index]

        
    def execute(self, obj):
        """ Create compound part at recompute. """

        if obj.ForceTypes == "Spring":
            p = 2
            h = dist(obj.JointCoord1,obj.JointCoord2)
            r = 1.5
    
            creation_axis = FreeCAD.Vector(0,0,1)
            desired_direction = normalized(self.JointCoord2 - self.JointCoord1)
            angle = degrees(acos(dotproduct(creation_axis, desired_direction)))
            axis = crossproduct(creation_axis,desired_direction)
            helix = Part.makeHelix(p,h,r)
            helix.Placement.Base = self.JointCoord1
            helix.rotate(self.JointCoord1,axis,angle) 
            obj.Shape = helix
        
        else:
            obj.Shape = Part.Shape()
            
        return 

    def rebuildInputs(self,index):

        if index == 0:    
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            self.Joint2 = self.obj.Joint2
            self.JointCoord1 = self.obj.JointCoord1
            self.JointCoord2 = self.obj.JointCoord2

            self.form.lcsName1.setText(self.Joint1)
            self.form.lcsName2.setText(self.Joint2)

            self.execute(self.obj)

        elif index == 1:
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            self.JointCoord1 = self.obj.JointCoord1

            self.form.lcsName3.setText(self.Joint1)
            
        elif index == 2:
            self.Point = self.obj.Point
            self.Body = self.obj.Body 
            self.PointCoord = self.obj.PointCoord

            self.form.pointName.setText(self.Point)

        return


    def accept(self,index):
        if index == 0:
            self.obj.Body1 = self.Body1
            self.obj.Body2 = self.Body2
            self.obj.Joint1 = self.Joint1
            self.obj.Joint2 = self.Joint2
            self.obj.JointCoord1 = self.JointCoord1
            self.obj.JointCoord2 = self.JointCoord2

        elif index == 1:
            self.obj.Body1 = self.Body1
            self.obj.Body2 = self.Body2
            self.obj.Joint1 = self.Joint1
            self.obj.JointCoord1 = self.JointCoord1        

        elif index == 2:       
            self.obj.Point = self.Point
            self.obj.Body = self.Body
            self.obj.PointCoord = self.PointCoord
        
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.recompute()
        doc_name = str(self.obj.Document.Name)        
        FreeCAD.getDocument(doc_name).recompute()
        return 

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.recompute()
        doc_name = str(self.obj.Document.Name)        
        FreeCAD.getDocument(doc_name).recompute()
        return 

    def selectedBody1(self,_index):
        
        if _index == 0:
            index = self.form.body1Combo.currentIndex()
            self.Body1 = self.body_labels[index]

        elif _index == 1:
            index = self.form.body1Combo_2.currentIndex()
            self.Body1 = self.body_labels[index]

        elif _index == 2:
            index = self.form.bodyPointCombo.currentIndex()
            self.Body = self.body_labels[index]

        self.selectObjectInGui(index)

    def selectedBody2(self,_index):
    
        if _index == 0:
            index = self.form.body2Combo.currentIndex()
            self.Body2 = self.body_labels[index]
        elif _index == 1:
            index = self.form.body2Combo_2.currentIndex()
            self.Body2 = self.body_labels[index]

        self.selectObjectInGui(index)

    def selectObjectInGui(self, index):
        FreeCADGui.Selection.clearSelection()
        #FreeCAD.Console.PrintMessage(self.body_labels[index])
        if self.body_objects[index] != None:
            FreeCADGui.showObject(self.body_objects[index])
            FreeCADGui.Selection.addSelection(self.body_objects[index])
    
    def selectInGui(self):

        if self.buttonName == "LCS" or self.buttonName == "Point":

            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(self.Point)[0]
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object)

        elif self.buttonName == "Vertex":
           
            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(self.BodyPoint)[0]
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object,self.Point)

    def selectLCSinGui(self,joint):
        FreeCADGui.Selection.clearSelection()
        docName = str(self.doc_name)
        doc = FreeCAD.getDocument(docName)
        selection_object = doc.getObjectsByLabel(joint)[0]
        FreeCADGui.showObject(selection_object)
        FreeCADGui.Selection.addSelection(selection_object)
            
    def addLCS1(self,index):
        sel = FreeCADGui.Selection.getSelectionEx()
        updated = False
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected when defining co-ordinate.")
        else:
            if "LCS" in sel[0].Object.Name:
                if index == 0:
                    self.form.lcsName1.setText(sel[0].Object.Label)
                    self.Joint1 = sel[0].Object.Label
                    self.JointCoord1 = sel[0].Object.Placement.Base

                elif index == 1:
                    self.form.lcsName3.setText(sel[0].Object.Label)
                    self.Joint1 = sel[0].Object.Label
                    self.JointCoord1 = sel[0].Object.Placement.Base
                    updated = True
                if self.Joint2 != "":
                    updated = True
        if updated:
            self.obj.recompute()
            doc_name = str(self.obj.Document.Name)        
            FreeCAD.getDocument(doc_name).recompute()
            self.obj.recompute()
        
            
    def addLCS2(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected.")
        else:
            if "LCS" in sel[0].Object.Name:
                self.form.lcsName2.setText(sel[0].Object.Label)       
                self.Joint2 = sel[0].Object.Label
                self.JointCoord2 = sel[0].Object.Placement.Base

                if self.Joint1 != "":
                    self.obj.recompute()
                    doc_name = str(self.obj.Document.Name)        
                    FreeCAD.getDocument(doc_name).recompute()
                    self.obj.recompute()

    def addPoint(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single point,LCS or Vertex needs to be selected")
        else:
            if "LCS" in sel[0].Object.Name:
                self.form.pointName.setText(sel[0].Object.Label)
                self.Point = sel[0].Object.Label
                self.PointCoord = sel[0].Object.Placement.Base
                self.buttonName = "LCS"
               
            elif "Point" in sel[0].Object.Name:
                self.form.pointName.setText(sel[0].Object.Label)
                self.Point = sel[0].Object.Label
                self.PointCoord = sel[0].Object.Placement.Base
                self.buttonName = "Point"

            elif "Vertex" in sel[0].SubElementNames[0]:
                self.form.pointName.setText(sel[0].SubElementNames[0])
                self.BodyPoint = sel[0].Object.Label 
                self.Point = sel[0].SubElementNames[0]
                self.PointCoord = sel[0].SubObjects[0].Point
                self.buttonName = "Vertex"
  
    def closing(self):
        """ Call this on close to let the widget to its proper cleanup """
        FreeCADGui.Selection.removeObserver(self)















        

