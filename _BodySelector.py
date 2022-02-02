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
    import PySide
import Part
import math
from math import degrees,acos
import _FreeCADVectorTools
from _FreeCADVectorTools import dist, normalized, crossproduct,dotproduct, angle, length


TYPES = ["two points and two bodies","One point and two bodies","One Point and associated point" ]

HELPER_TEXT = ["Choose two points (LCS) and two bodies, where the points belong to the corresponding body",
               "Choose one point (LCS) and two bodies",
               "Add points for post-processing. Pick one point and the body associated to it" ]

class BodySelector:
    def __init__(self, parent_widget, obj):
        ui_path = os.path.join(os.path.dirname(__file__), "BodySelector.ui")
        self.parent_widget = parent_widget
        self.form = FreeCADGui.PySideUic.loadUi(ui_path, self.parent_widget)
        self.parent_widget.layout().addWidget(self.form)

        addObjectProperty(obj,"JointType",TYPES, "App::PropertyEnumeration", "", "Joint Types")
        
        self.obj = obj
        self.obj.setEditorMode("JointType", 2)

            
        self.doc_name = self.obj.Document.Name
        self.view_object = self.obj.ViewObject

        active_analysis = DapTools.getActiveAnalysis()
        self.body_labels = ["Ground"]
        self.body_objects = [None]
        for i in active_analysis.Group:
            if "DapBody" in i.Name:
                self.body_labels.append(i.Label)
                self.body_objects.append(i)

    def close(self):
        """closes the widget"""
        self.form.inputWidget.setCurrentIndex(-1) 

    # index == 0

    def Page1(self):
        """2 Points 2 Bodies """
        index = 0
        self.form.page1.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Preferred)
        self.form.page2.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page3.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page4.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)

        self.form.body1Combo.clear()
        self.form.body1Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.body1Combo.setCurrentIndex(b1i)
        self.selectedBody1(_index = index)

        self.form.body2Combo.clear()
        self.form.body2Combo.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.body2Combo.setCurrentIndex(b1i)
        self.selectedBody2(_index = index)

        self.form.lcsPush1.clicked.connect(lambda: self.addLCS1(index))
        self.form.lcsPush2.clicked.connect(self.addLCS2)

        self.form.lcsName1.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint1))
        self.form.lcsName2.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint2))        
        
        self.form.body1Combo.currentIndexChanged.connect(lambda: self.selectedBody1(_index = index))
        self.form.body2Combo.currentIndexChanged.connect(lambda: self.selectedBody2(_index = index))

        self.rebuildInputs(index)
        
        self.comboTypeChanged()

        return 
    
        
# index == 1
    def Page2(self):
        """1 point 2 bodies """
        index = 1
        self.form.page1.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page2.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Preferred)
        self.form.page3.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page4.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)
    

        self.form.body1Combo_2.clear()
        self.form.body1Combo_2.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body1, 0)
        self.form.body1Combo_2.setCurrentIndex(b1i)
        self.selectedBody1(_index = index)
        
        self.form.body2Combo_2.clear()
        self.form.body2Combo_2.addItems(self.body_labels)
        b1i = indexOrDefault(self.body_labels, self.obj.Body2, 0)
        self.form.body2Combo_2.setCurrentIndex(b1i)
        self.selectedBody2(_index = index)

        self.form.lcsPush3.clicked.connect(lambda : self.addLCS1(index))
        self.form.lcsName3.clicked.connect(lambda : self.selectLCSinGui(self.obj.Joint1))

        #NOTE to Varnu, when indexChanged even is called, an index is passed through to the function
        self.form.body1Combo_2.currentIndexChanged.connect(lambda: self.selectedBody1(_index = index))
        self.form.body2Combo_2.currentIndexChanged.connect(lambda: self.selectedBody2(_index = index))

        self.rebuildInputs(index)

        self.comboTypeChanged()

        return 

    # index == 2
    def Page3(self):
        """Points selection """
        index = 2
        self.form.page1.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page2.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        self.form.page3.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Preferred)
        self.form.page4.setSizePolicy(PySide.QtGui.QSizePolicy.Expanding, PySide.QtGui.QSizePolicy.Ignored)
        
        self.form.inputWidget.setCurrentIndex(index)
        self.PageInit(index)
       
        self.form.pointPush.clicked.connect(self.addPoint)

        self.form.pointName.clicked.connect(self.selectInGui)

        self.form.pointList.itemClicked.connect(self.selectInGui2)

        self.form.pointRemove.clicked.connect(self.buttonRemovePointClicked)

        self.rebuildInputs(index)

        self.comboTypeChanged()

        return 

    def emptyPage(self):
        """ Empty page if nothing should be selected"""
        index = 3
        self.form.inputWidget.setCurrentIndex(index)

    def PageInit(self,index):
        """assign local variables depending on the page selected """
        # self.index = self.form.inputWidget.currentIndex()
        if index == 0:
            # self.JType = self.obj.JointType 
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            self.Joint2 = self.obj.Joint2
            # self.JointCoord1 = self.obj.JointCoord1
            # self.JointCoord2 = self.obj.JointCoord2

            #adjustSize()

        elif index == 1:
            # self.JType = self.obj.JointType
            # self.Joint1 = self.obj.Joint1
            self.Body1 = self.obj.Body1
            self.Body2 = self.obj.Body2
            

        elif index == 2:
            # self.JType = self.obj.JointType
            self.Point = self.obj.Point 
            self.PointCoord = self.obj.PointCoord
            self.pointList = self.obj.pointList
            self.bodyNameList = self.obj.bodyNameList
            self.pointAssignList = self.obj.pointAssignList 
            self.pointCoordList = self.obj.pointCoordList 
            

    def comboTypeChanged(self):
        """used to change the helper text of body selected"""
        type_index = self.form.inputWidget.currentIndex()
        self.form.labelHelperText.setText(HELPER_TEXT[type_index])
        self.JType = TYPES[type_index]

        
    #def execute(self, obj,index):
        #""" Create compound part at recompute. """
        #if index == 0:

            #if obj.ForceTypes == "Spring":
                #p = 2
                #h = dist(obj.JointCoord1,obj.JointCoord2)
                #r = 1.5
        
                #creation_axis = FreeCAD.Vector(0,0,1)
                #desired_direction = normalized(self.JointCoord2 - self.JointCoord1)
                #angle = degrees(acos(dotproduct(creation_axis, desired_direction)))
                #axis = crossproduct(creation_axis,desired_direction)
                #helix = Part.makeHelix(p,h,r)
                #helix.Placement.Base = self.JointCoord1
                #helix.rotate(self.JointCoord1,axis,angle) 
                #obj.Shape = helix

            #else:
                #obj.Shape = Part.Shape()

        #elif index == 1:
            #obj.Shape = Part.Shape()

        #elif index == 2:
            #shape_list=[]
            #r = 0.1 
            #if len(self.pointCoordList)>0:
                #for i in range(len(obj.pointList)):
                     #point = Part.makeSphere(r)
                     #point.Placement.Base = self.pointCoordList[i]
                     #shape_list.append(point)
                #shape = Part.makeCompound(shape_list)
                #obj.Shape = shape
                
            #else:
                #obj.Shape = Part.Shape()
                
        #return None

    def rebuildInputs(self,index):
        """place previous inputs back into selection windows"""

        if index == 0:    
            #self.Body1 = self.obj.Body1
            #self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            self.Joint2 = self.obj.Joint2
            
            # self.JointCoord1 = self.obj.JointCoord1
            # self.JointCoord2 = self.obj.JointCoord2

            self.form.lcsName1.setText(self.Joint1)
            self.form.lcsName2.setText(self.Joint2)

        elif index == 1:
            #self.Body1 = self.obj.Body1
            #self.Body2 = self.obj.Body2
            self.Joint1 = self.obj.Joint1
            # self.JointCoord1 = self.obj.JointCoord1

            self.form.lcsName3.setText(self.Joint1)

        
        elif index == 2:
            self.Point = self.obj.Point
            self.PointCoord = self.obj.PointCoord
            self.bodyNameList = self.obj.bodyNameList
            self.pointAssignList = self.obj.pointAssignList
            self.pointCoordList = self.obj.pointCoordList

            self.form.pointName.setText("Select the LCS,point or vertex")

            self.rebuildPointList()
            
        return


    def accept(self,index):
        if index == 0:
            self.obj.Body1 = self.Body1
            self.obj.Body2 = self.Body2
            self.obj.Joint1 = self.Joint1
            self.obj.Joint2 = self.Joint2
            #self.obj.JointCoord1 = self.JointCoord1
            #self.obj.JointCoord2 = self.JointCoord2


        elif index == 1:
            self.obj.Body1 = self.Body1
            self.obj.Body2 = self.Body2
            self.obj.Joint1 = self.Joint1
            #self.obj.JointCoord1 = self.JointCoord1
       

        elif index == 2:       
            self.obj.Point = self.Point
            self.obj.PointCoord = self.PointCoord
            self.obj.pointList = self.pointList 
            self.obj.bodyNameList = self.bodyNameList
            self.obj.pointAssignList = self.pointAssignList
            self.obj.pointCoordList = self.pointCoordList

        
        
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        #self.obj.recompute()
        #doc_name = str(self.obj.Document.Name)        
        #FreeCAD.getDocument(doc_name).recompute()
        
        return 

    def reject(self, index = None):
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        if index == 0:
            # self.obj.JointCoord1 = self.JointCoord1
            a =1
            # self.obj.JointCoord2 = self.JointCoord2
        elif index == 1:
            a = 1
            # self.obj.JointCoord1 = self.JointCoord1
            
        self.obj.recompute()
        
        #doc_name = str(self.obj.Document.Name)        
        #FreeCAD.getDocument(doc_name).recompute()
        return 

    def selectedBody1(self, _index=0):
        updated = False 
        if _index == 0:
            index = self.form.body1Combo.currentIndex()
            self.obj.Body1 = self.body_labels[index]

        elif _index == 1:
            index = self.form.body1Combo_2.currentIndex()
            self.obj.Body1 = self.body_labels[index]

            if self.obj.Body2 != "":
                updated = True 

        elif _index == 2:
            index = self.form.bodyPointCombo.currentIndex()
            self.obj.Body = self.body_labels[index]

        self.selectObjectInGui(index)

        if updated:
            self.obj.recompute()

    def selectedBody2(self,_index=0):
        updated = False 
        if _index == 0:
            index = self.form.body2Combo.currentIndex()
            self.obj.Body2 = self.body_labels[index]
        elif _index == 1:
            index = self.form.body2Combo_2.currentIndex()
            self.obj.Body2 = self.body_labels[index]

            if self.obj.Body1 != "":
                updated = True  

        self.selectObjectInGui(index)

        if updated: 
            self.obj.recompute()

        

    def selectObjectInGui(self, index):
        """shows body selections in gui"""
        FreeCADGui.Selection.clearSelection()
        #FreeCAD.Console.PrintMessage(self.body_labels[index])
        if self.body_objects[index] != None:
            FreeCADGui.showObject(self.body_objects[index])
            FreeCADGui.Selection.addSelection(self.body_objects[index])
    
    
    def selectInGui2(self):
        """shows the points chosen from a combo box"""

        if "LCS" in self.form.pointList.currentItem().text() or "Point" in self.form.pointList.currentItem().text():

            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(self.form.pointList.currentItem().text())[0]
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object)

        elif "Vertex" in self.form.pointList.currentItem().text():
            index = self.pointAssignList.index(self.form.pointList.currentItem().text())
            point = self.pointList[index]
            body = self.bodyNameList[index]
           
            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObject(body)
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object,point)
    

    def selectInGui(self):
        """shows the points chosen from the selection window"""
        
        if "LCS" in self.Point or "Point" in self.Point:

            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(self.Point)[0]
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object)

        elif "Vertex" in self.Point:
           
            FreeCADGui.Selection.clearSelection()
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)

            selection_object = doc.getObjectsByLabel(self.BodyPoint)[0]
            FreeCADGui.showObject(selection_object)
            FreeCADGui.Selection.addSelection(selection_object,self.Point)

    def selectLCSinGui(self,joint):
        "used to show the LCS from a selection window"

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
                    self.obj.Joint1 = sel[0].Object.Label
                    self.obj.JointCoord1 = sel[0].Object.Placement.Base
                    FreeCAD.Console.PrintError(self.obj.JointCoord1)
                    if self.obj.Joint2 != "":
                        updated = True

                elif index == 1:
                    self.form.lcsName3.setText(sel[0].Object.Label)
                    self.obj.Joint1 = sel[0].Object.Label
                    self.obj.JointCoord1 = sel[0].Object.Placement.Base
                    updated = True
                

        if updated:
            #self.execute(self.obj,0)
            #TODO reset the coord on cancel
            #self.obj.JointCoord1 = self.JointCoord1
            self.obj.recompute()
            #doc_name = str(self.obj.Document.Name)        
            #FreeCAD.getDocument(doc_name).recompute()
            
    def addLCS2(self):

        sel = FreeCADGui.Selection.getSelectionEx()

        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single face, or single LCS should be selected.")

        else:
            if "LCS" in sel[0].Object.Name:
                self.form.lcsName2.setText(sel[0].Object.Label)       
                self.obj.Joint2 = sel[0].Object.Label
                self.obj.JointCoord2 = sel[0].Object.Placement.Base
                FreeCAD.Console.PrintError(self.obj.JointCoord2)

                if self.obj.Joint1 != "":
                    #self.execute(self.obj,0)
                    #TODO reset the coord on cancel
                    #self.obj.JointCoord2 = self.JointCoord2
                    self.obj.recompute()
                    #doc_name = str(self.obj.Document.Name)        
                    #FreeCAD.getDocument(doc_name).recompute()
    
    def addPoint(self):
        sel = FreeCADGui.Selection.getSelectionEx()
        
        if len(sel)>1 or len(sel[0].SubElementNames)>1:
            FreeCAD.Console.PrintError("Only a single point,LCS or Vertex needs to be selected")

        else:
            if "LCS" in sel[0].Object.Name:
                self.form.pointName.setText(sel[0].Object.Label)
                self.Point = sel[0].Object.Label
                self.PointCoord = sel[0].Object.Placement.Base
                self.bodyNameList.append("")
                self.pointList.append("")
                
                if self.Point not in self.pointAssignList:
                    self.pointAssignList.append(self.Point)
                    self.pointCoordList.append(self.PointCoord)


            elif "Point" in sel[0].Object.Name:
                self.form.pointName.setText(sel[0].Object.Label)
                self.Point = sel[0].Object.Label
                self.PointCoord = sel[0].Object.Placement.Base
                self.bodyNameList.append("")
                self.pointList.append("")
                

                if self.Point not in self.pointAssignList:
                    self.pointAssignList.append(self.Point)
                    self.pointCoordList.append(self.PointCoord)
                    
               
            elif "Vertex" in sel[0].SubElementNames[0]:
                self.form.pointName.setText(sel[0].SubElementNames[0])
                self.BodyPoint = sel[0].Object.Label
                self.BodyName = sel[0].Object.Name  
                self.Point = sel[0].SubElementNames[0]
                self.PointCoord = sel[0].SubObjects[0].Point

                if (self.Point + "" + self.BodyName) not in self.pointAssignList:
                    self.pointList.append(self.Point)
                    self.pointAssignList.append(self.Point + "" + self.BodyName)
                    self.bodyNameList.append(self.BodyName)
                    self.pointCoordList.append(self.PointCoord)

        self.form.pointList.clear()
        for i in range(len(self.pointAssignList)):
            self.form.pointList.addItem(self.pointAssignList[i])
          
  
    def buttonRemovePointClicked(self):
        
        if not self.pointAssignList:
            return

        if not self.form.pointList.currentItem():
            return
        
        row = self.form.pointList.currentRow()
        self.pointAssignList.pop(row)
        self.pointCoordList.pop(row)
        self.form.pointList.takeItem(row)

    def rebuildPointList(self):
        self.form.pointList.clear()
        for i in range(len(self.pointAssignList)):
            self.form.pointList.addItem(self.pointAssignList[i])

    def closing(self):
        """ Call this on close to let the widget to its proper cleanup """
        self.form.inputWidget.setCurrentIndex(-1)
        FreeCADGui.Selection.removeObserver(self)















        

