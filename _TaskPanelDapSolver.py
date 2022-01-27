 
 




#TODO Include license


from importlib.resources import path
import FreeCAD
from FreeCAD import Units
import os
import os.path
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapBodySelection
import DapSolverBuilder
import DapSolverRunner
import numpy as np
import math
import time
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapSolver:
    """ Taskpanel for Executing DAP Solver User Interface """
    def __init__(self, obj):
        self.obj = obj
        self.doc_name = self.obj.Document.Name
        self.FileDirectory = self.obj.FileDirectory
        self.MotionPlane = self.obj.MotionPlane
        self.SelectionType = self.obj.SelectionType
        self.ObjectEntities = self.obj.ObjectEntities
        self.XVector = self.obj.XVector
        self.YVector = self.obj.YVector
        self.ZVector = self.obj.ZVector
        self.UnitVector = self.obj.UnitVector
        self.PlaneObjectName = self.obj.PlaneObjectName

        self.face_count = 0

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapRunner.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.form.cmbPlaneofMotion.addItems(DapSolverRunner.MOTION_PLANES)

        self.form.cmbSelectType.addItems(DapSolverRunner.SELECTION_TYPE)

        # On reload, check to see if item already exists, and set dropbox item appropriately for both Comboboxes
        biMotionPlane = indexOrDefault(DapSolverRunner.MOTION_PLANES, self.obj.MotionPlane, 0)
        self.form.cmbPlaneofMotion.setCurrentIndex(biMotionPlane)
        self.form.lblPlaneDescr.setText(DapSolverRunner.MOTION_PLANES_HELPER_TEXT[biMotionPlane])

        biSelectType = indexOrDefault(DapSolverRunner.SELECTION_TYPE, self.obj.SelectionType, 0)
        self.form.cmbSelectType.setCurrentIndex(biSelectType)
        self.form.lblSelectDescr.setText(DapSolverRunner.SELECTION_TYPE_HELPER_TEXT[biSelectType])

        self.form.solveButton.clicked.connect(self.solveButtonClicked)

        self.form.pbBrowseFileDirectory.clicked.connect(self.getFolderDirectory)

        self.form.pbAddRef.clicked.connect(self.addButtonClicked)

        self.form.pbRemoveRef.clicked.connect(self.removeButtonClicked)

        self.form.dsbVeci.valueChanged.connect(self.xChanged)
        self.form.dsbVecj.valueChanged.connect(self.yChanged)
        self.form.dsbVeck.valueChanged.connect(self.zChanged)
        

        self.form.cmbPlaneofMotion.currentIndexChanged.connect(self.cmbPlaneChanged)

        self.form.cmbSelectType.currentIndexChanged.connect(self.cmbSelectChanged)
        
        self.form.selectPlanarObjectButton.clicked.connect(self.customObjectSelection)

        self.rebuildObjectList()

        self.rebuildConditions()
        
        self.setTimeValueOnReload()

        self.checkPlane()

        #self.checkSelectType()

    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()

        self.checkPlane()
        
        self.obj.MotionPlane = self.MotionPlane
        self.obj.SelectionType = self.SelectionType
        self.obj.ObjectEntities = self.ObjectEntities
        self.obj.XVector = self.UnitVector.x
        self.obj.YVector = self.UnitVector.y
        self.obj.ZVector = self.UnitVector.z
        self.obj.UnitVector = self.UnitVector
        
        self.getTimeValues()

        return

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def setTimeValueOnReload(self):
        self.form.startTime.setValue(self.obj.StartTime)
        self.form.endTime.setValue(self.obj.EndTime)
        self.form.reportingTime.setValue(self.obj.ReportingTimeStep)

    def getTimeValues(self):
        self.obj.StartTime = self.form.startTime.value()
        self.obj.EndTime = self.form.endTime.value()
        self.obj.ReportingTimeStep = self.form.reportingTime.value()

    def checkValidityOfTime(self):
        if self.obj.StartTime > self.obj.EndTime:
            raise RuntimeError("Start time is greater than end time")
        if self.obj.ReportingTimeStep > self.obj.EndTime:
            raise RuntimeError("Reporting time is greater than end time")

    def solveButtonClicked(self):
        #builder = DapSolverBuilder.DapSolverBuilder()
        self.obj.MotionPlane = self.MotionPlane
        self.obj.SelectionType = self.SelectionType
        self.obj.ObjectEntities = self.ObjectEntities

        self.obj.FileDirectory = self.form.lnedFileDirectory.text()

        #if self.obj.FileDirectory == "":
            #FreeCAD.Console.PrintError("\n Warning!!  No file directory chosen for saving Results \n")
            #self.defaultFileDirectory()
            #FreeCAD.Console.PrintError("\n The above folder has been chosen as the default directory \n")

        self.checkPlane()

        self.obj.XVector = self.UnitVector.x
        self.obj.YVector = self.UnitVector.y
        self.obj.ZVector = self.UnitVector.z
        self.obj.UnitVector = self.UnitVector

        self.printUnitVector()
        
        self.getTimeValues()
        self.checkValidityOfTime()
        
        
        self.builder = DapSolverBuilder.DapSolverBuilder(self.obj)

        
        FreeCAD.Console.PrintMessage("DAP SOLVER STARTED \n")

        self.builder.writeInputFiles()
        self.builder.solve()
        
        #builder.computeCentreOfGravity()

    def cmbPlaneChanged(self): #Mod
        type_index = self.form.cmbPlaneofMotion.currentIndex()
        self.form.lblPlaneDescr.setText(DapSolverRunner.MOTION_PLANES_HELPER_TEXT[type_index])
        self.MotionPlane = DapSolverRunner.MOTION_PLANES[type_index]
        self.checkPlane()
        self.rebuildConditions()

    def cmbSelectChanged(self):
        type_index = self.form.cmbSelectType.currentIndex()
        self.form.lblSelectDescr.setText(DapSolverRunner.SELECTION_TYPE_HELPER_TEXT[type_index])
        self.SelectionType = DapSolverRunner.SELECTION_TYPE[type_index]
        self.checkSelectType()
        self.rebuildConditions()
        return

    def addButtonClicked(self):
        sel = FreeCADGui.Selection.getSelectionEx()[0]
        sel_name = sel.SubElementNames

        for i in range(0, len(sel_name)):
            if sel_name[i] in self.ObjectEntities:
                FreeCAD.Console.PrintError("\n Error:  The selected object has already been referenced \n")
            else:
                self.ObjectEntities.append(sel_name[i])

        self.rebuildObjectList()
        return

    def removeButtonClicked(self):
        if not self.ObjectEntities:
            FreeCAD.Console.PrintMessage("Here 1")
            return
        if not self.form.lstObjectEntities.currentItem():
            FreeCAD.Console.PrintMessage("Here 2")
            return
        row = self.form.lstObjectEntities.currentRow()
        self.ObjectEntities.pop(row)
        self.rebuildObjectList()
        self.rebuildConditions()
        return

    def defaultFileDirectory(self):
        self.FileDirectory = os.getcwd()
        #FreeCAD.Console.PrintMessage(self.obj.FileDirectory)
        self.form.lnedFileDirectory.setText(self.FileDirectory)
        return

    def getFolderDirectory(self):
        self.obj.FileDirectory = QtGui.QFileDialog.getExistingDirectory()
        self.form.lnedFileDirectory.setText(self.obj.FileDirectory)
        return

    def checkPlane(self):
        if self.MotionPlane == "X-Y Plane" or self.MotionPlane == "Y-Z Plane" or self.MotionPlane == "X-Z Plane":
            if self.MotionPlane == "X-Y Plane":
                self.XVector = 0.0
                self.YVector = 0.0
                self.ZVector = 1.0
            elif self.MotionPlane == "Y-Z Plane":
                self.XVector = 1.0
                self.YVector = 0.0
                self.ZVector = 0.0
            else:
                self.XVector = 0.0
                self.YVector = 1.0
                self.ZVector = 0.0
                
            if (self.XVector != 0) or (self.YVector != 0) or (self.ZVector != 0):
                mag = (self.XVector**2 + self.YVector**2 + self.ZVector**2)**0.5        
                rounder = 3        
                self.UnitVector = FreeCAD.Vector(round(self.XVector/mag, rounder), 
                                                 round(self.YVector/mag, rounder),
                                                 round(self.ZVector/mag, rounder))
            
            self.form.lblPlaneSelectType.setHidden(True)
            self.form.cmbSelectType.setHidden(True)
            self.form.lblDescription2.setHidden(True)
            self.form.lblSelectDescr.setHidden(True)
            self.form.lblEntitySelect.setHidden(True)
            self.form.stWidg.setHidden(True)
            #self.form.lblPlaneDefined.setText("Plane of Motion successfully defined")
            self.obj.setEditorMode("ObjectEntities", 2)
            self.obj.setEditorMode("XVector", 2)
            self.obj.setEditorMode("YVector", 2)
            self.obj.setEditorMode("ZVector", 2)

        if self.MotionPlane == "Custom Plane...":
            self.form.lblPlaneSelectType.setHidden(False)
            self.form.cmbSelectType.setHidden(False)
            self.form.lblDescription2.setHidden(False)
            self.form.stWidg.setHidden(False)
            self.form.lblSelectDescr.setHidden(False)
            self.form.lblEntitySelect.setHidden(False)
            #self.form.lblPlaneDefined.setText("No Plane of Motion could be Generated from the Information Provided")
            self.obj.setEditorMode("ObjectEntities", 0)
            self.checkSelectType()

        return

    def customObjectSelection(self):
        
        sel = FreeCADGui.Selection.getSelectionEx()
        if len(sel)>0:
            if len(sel)>1 or len(sel[0].SubElementNames)>1:
                FreeCAD.Console.PrintError("Only a single face, sketch or plane should be selected.\n")
            else:
                changed = False
                if len(sel[0].SubElementNames) == 1:
                    if 'Face' in sel[0].SubElementNames[0]:
                        face = sel[0].Object.getSubObject(sel[0].SubElementNames[0])
                        normal = face.normalAt(0,0)
                        
                        self.form.planarObjectLabel.setText(sel[0].Object.Label+":"+str(sel[0].SubElementNames[0]))
                        
                        changed = True
                        
                elif sel[0].Object.TypeId == 'Sketcher::SketchObject':
                    support_name = sel[0].Object.Support[0][0].Name
                    sub_shape = sel[0].Object.Support[0][1]
                    if "XY_Plane" in support_name:
                        #FreeCAD.Console.PrintMessage("YES XY PLANE \n")
                        normal = FreeCAD.Vector(0,0,1)
                        changed = True
                    if "XZ_Plane" in support_name:
                        normal = FreeCAD.Vector(0,1,0)
                        changed = True
                    if "YZ_Plane" in support_name:
                        normal = FreeCAD.Vector(1,0,0)
                        changed = True
                    if "Face" in sub_shape[0]:
                        face = sel[0].Object.Support[0][0].getSubObject(sub_shape[0])
                        normal = face.normalAt(0,0)
                        changed = True
                elif sel[0].Object.TypeId == 'Part::Plane':
                    normal = sel[0].Object.Shape.Faces[0].normalAt(0,0)
                    changed = True
                elif sel[0].Object.TypeId == 'App::Plane':
                    role = sel[0].Object.Role
                    if "XY_Plane" in role:
                        normal = FreeCAD.Vector(0,0,1)
                        changed = True
                    if "XZ_Plane" in role:
                        normal = FreeCAD.Vector(0,1,0)
                        changed = True
                    if "YZ_Plane" in role:
                        normal = FreeCAD.Vector(1,0,0)
                        changed = True
                else:
                    FreeCAD.Console.PrintError("Can not idenitfy normal from " + str(sel[0].Object.Label) + "object \n")
                    
                if changed:
                    self.XVector = normal.x
                    self.YVector = normal.y
                    self.ZVector = normal.z
                    #vector = FreeCAD.Vector(self.XVector, self.YVector, self.ZVector)
                    self.UnitVector = normal
                    
                    self.printUnitVector()
        else:
            FreeCAD.Console.PrintMessage("Nothing was selected \n")

    def checkSelectType(self):
        """Determine the planar properties from either the features selected or the normal vector definition"""
        self.form.stWidg.setCurrentIndex(0)
        self.form.planarObjectLabel.setText(self.PlaneObjectName)
        
         # NOTE: Previous object selection written by Dewald.
         # simplifying selection for now to only allow face, plane or sketch
        #if self.SelectionType == "Object Selection":
            #self.form.stWidg.setCurrentIndex(0)

            #self.obj.setEditorMode("ObjectEntities", 0)
            #self.obj.setEditorMode("XVector", 2)
            #self.obj.setEditorMode("YVector", 2)
            #self.obj.setEditorMode("ZVector", 2)


            #if (len(self.ObjectEntities) == 1) and ("Face" in self.ObjectEntities[0]):
                #self.form.lblPlaneDefined.setText("Planar Motion successfully defined via coincident face")
            ##     sel = FreeCADGui.Selection.getSelectionEx()[0]
            ##     sel_entity = sel.Object.Name
            ##     face_entity = sel.Object.SubElementNames[0]
            ##     FreeCAD.Console.PrintMessage(face_entity)
            ##     FreeCAD.Console.PrintMessage("\n \n")
            ##     FreeCAD.Console.PrintMessage(sel_entity)
            ##     element_char = FreeCAD.ActiveDocument.getObject(str(sel_entity)).Shape.face_entity
            ##     elt_planar = element_char.Surface.isPlanar()
            ##     if elt_planar:
            ##         self.form.lblPlaneDefined.setText("Planar motion successfully defined via coincident face")
            ##     else:
            ##         self.form.lblPlaneDefined.setText("Selected face is non-planar.  Cannot generate coincident plane")

            #if len(self.ObjectEntities) > 1:
                #face_counter = 0
                #for i in range(0, len(self.ObjectEntities)):
                    #if "Face" in self.ObjectEntities[i]:
                        #face_counter = face_counter + 1
                #if face_counter > 0:
                    #FreeCAD.Console.PrintError("\n Error!!  Face has been defined in tandem with other features \n")
                    #FreeCAD.Console.PrintError(self.ObjectEntities)
                    #FreeCAD.Console.PrintError("\n Review above object list for redundancy")
                    #self.form.lblPlaneDefined.setText("Planar motion could not be defined.  Check error messages")


                #if face_counter == 0:
                    #edge_counter = 0
                    #vertex_counter = 0
                    #for j in range(0, len(self.ObjectEntities)):
                        #if "Edge" in self.ObjectEntities[j]:
                            #edge_counter = edge_counter + 1
                        #elif "Vertex" in self.ObjectEntities[j]:
                            #vertex_counter = vertex_counter + 1
                    #if (edge_counter == 2) and (len(self.ObjectEntities) == 2):
                        #self.form.lblPlaneDefined.setText("Planar motion set to be coincident with two lines")
                    #elif (edge_counter == 1) and (vertex_counter == 1) and(len(self.ObjectEntities) == 2):
                        #self.form.lblPlaneDefined.setText("Planar motion set to be coincident with a line and point")
                    #elif (vertex_counter == 3) and (len(self.ObjectEntities) == 3):
                        #self.form.lblPlaneDefined.setText("Planar motion set to be coincident with a set of 3 points")
                    #else:
                        #self.form.lblPlaneDefined.setText("Planar motion could not be defined from the given entities")
                        #FreeCAD.Console.PrintError("\n Plane of motion could not be defined from the given entites \n")
                        #FreeCAD.Console.PrintWarning(self.ObjectEntities)
                        #FreeCAD.Console.PrintError("\n Select face, 2 lines, line and point or set of three points \n")

        if self.SelectionType == "Object Selection":
            self.form.stWidg.setCurrentIndex(2)
            
        else:
            self.form.stWidg.setCurrentIndex(1)

            self.obj.setEditorMode("ObjectEntities", 2)
            self.obj.setEditorMode("XVector", 0)
            self.obj.setEditorMode("YVector", 0)
            self.obj.setEditorMode("ZVector", 0)

    def rebuildObjectList(self):
        self.form.lstObjectEntities.clear()
        for i in range(0, len(self.ObjectEntities)):
            self.form.lstObjectEntities.addItem(self.ObjectEntities[i])
        return

    def rebuildConditions(self):
        if self.FileDirectory == "":
            self.defaultFileDirectory()
        self.form.lnedFileDirectory.setText(self.FileDirectory)
        self.form.dsbVeci.setValue(self.XVector)
        self.form.dsbVecj.setValue(self.YVector)
        self.form.dsbVeck.setValue(self.ZVector)
        self.printUnitVector()
        return

    def xChanged(self):
        self.XVector = self.form.dsbVeci.value()
        self.unitVector()
    
    def yChanged(self):
        self.YVector = self.form.dsbVecj.value()
        self.unitVector()
    
    def zChanged(self):
        self.ZVector = self.form.dsbVeck.value()
        self.unitVector()

    def unitVector(self):
        """ Calculate the unit vector based on user inputs"""
        vector = FreeCAD.Vector(self.XVector,self.YVector,self.ZVector)
        if vector.Length != 0:
            vector.normalize()
            self.UnitVector = vector
            self.printUnitVector()
        else:
            FreeCAD.Console.PrintError("Vector of 0 length specified. \n")

        return
        
    def printUnitVector(self):
        self.form.lblUnitVecOut.setText("{:5.2f}{:5.2f}{:5.2f}".format(self.UnitVector.x,
                                                                        self.UnitVector.y,
                                                                        self.UnitVector.z))
        
