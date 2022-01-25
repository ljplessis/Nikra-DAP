 
 




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

        self.form.dsbVeci.valueChanged.connect(self.unitVector)
        self.form.dsbVecj.valueChanged.connect(self.unitVector)
        self.form.dsbVeck.valueChanged.connect(self.unitVector)

        self.form.cmbPlaneofMotion.currentIndexChanged.connect(self.cmbPlaneChanged)

        self.form.cmbSelectType.currentIndexChanged.connect(self.cmbSelectChanged)

        self.rebuildObjectList()

        self.rebuildConditions()

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

        return

    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    def solveButtonClicked(self):
        #builder = DapSolverBuilder.DapSolverBuilder()
        self.obj.MotionPlane = self.MotionPlane
        self.obj.SelectionType = self.SelectionType
        self.obj.ObjectEntities = self.ObjectEntities

        self.obj.FileDirectory = self.form.lnedFileDirectory.text()

        if self.obj.FileDirectory == "":
            FreeCAD.Console.PrintError("\n Warning!!  No file directory chosen for saving Results \n")
            self.defaultFileDirectory()
            FreeCAD.Console.PrintError("\n The above folder has been chosen as the default directory \n")

        self.checkPlane()

        self.obj.XVector = self.XVector
        self.obj.YVector = self.YVector
        self.obj.ZVector = self.ZVector

        self.form.lblUnitVecOut.setText(str(self.obj.UnitVector))

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
        self.obj.FileDirectory = os.getcwd()
        FreeCAD.Console.PrintMessage(self.obj.FileDirectory)
        self.form.lnedFileDirectory.setText(self.obj.FileDirectory)
        return

    def getFolderDirectory(self):
        self.obj.FileDirectory = QtGui.QFileDialog.getExistingDirectory()
        self.form.lnedFileDirectory.setText(self.obj.FileDirectory)
        return

    def checkPlane(self):

        if self.MotionPlane == "X-Y Plane" or "Y-Z Plane" or "X-Z Plane":

            self.form.lblPlaneSelectType.setHidden(True)
            self.form.cmbSelectType.setHidden(True)
            self.form.lblDescription2.setHidden(True)
            self.form.lblSelectDescr.setHidden(True)
            self.form.lblEntitySelect.setHidden(True)
            self.form.stWidg.setHidden(True)
            self.form.lblPlaneDefined.setText("Plane of Motion successfully defined")
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
            self.form.lblPlaneDefined.setText("No Plane of Motion could be Generated from the Information Provided")
            self.obj.setEditorMode("ObjectEntities", 0)
            self.checkSelectType()

        return

    def checkSelectType(self):
        """Determine the planar properties from either the features selected or the normal vector definition"""
        self.form.stWidg.setCurrentIndex(0)

        if self.SelectionType == "Object Selection":
            self.form.stWidg.setCurrentIndex(0)

            self.obj.setEditorMode("ObjectEntities", 0)
            self.obj.setEditorMode("XVector", 2)
            self.obj.setEditorMode("YVector", 2)
            self.obj.setEditorMode("ZVector", 2)


            # if (len(self.ObjectEntities) == 1) and ("Face" in self.ObjectEntities[0]):
            #     sel = FreeCADGui.Selection.getSelectionEx()[0]
            #     sel_entity = sel.Object.Name
            #     face_entity = sel.Object.SubElementNames[0]
            #     FreeCAD.Console.PrintMessage(face_entity)
            #     FreeCAD.Console.PrintMessage("\n \n")
            #     FreeCAD.Console.PrintMessage(sel_entity)
            #     element_char = FreeCAD.ActiveDocument.getObject(str(sel_entity)).Shape.face_entity
            #     elt_planar = element_char.Surface.isPlanar()
            #     if elt_planar:
            #         self.form.lblPlaneDefined.setText("Planar motion successfully defined via coincident face")
            #     else:
            #         self.form.lblPlaneDefined.setText("Selected face is non-planar.  Cannot generate coincident plane")

            if len(self.ObjectEntities) > 1:
                face_counter = 0
                for i in range(0, len(self.ObjectEntities)):
                    if "Face" in self.ObjectEntities[i]:
                        face_counter = face_counter + 1
                if face_counter > 0:
                    FreeCAD.Console.PrintError("\n Error!!  Face has been defined in tandem with other features \n")
                    FreeCAD.Console.PrintError(self.ObjectEntities)
                    FreeCAD.Console.PrintError("\n Review above object list for redundancy")
                    self.form.lblPlaneDefined.setText("Planar motion could not be defined.  Check error messages")


                if face_counter == 0:
                    edge_counter = 0
                    vertex_counter = 0
                    for j in range(0, len(self.ObjectEntities)):
                        if "Edge" in self.ObjectEntities[j]:
                            edge_counter = edge_counter + 1
                        elif "Vertex" in self.ObjectEntities[j]:
                            vertex_counter = vertex_counter + 1
                    if (edge_counter == 2) and (len(self.ObjectEntities) == 2):
                        self.form.lblPlaneDefined.setText("Planar motion set to be coincident with two lines")
                    elif (edge_counter == 1) and (vertex_counter == 1) and(len(self.ObjectEntities) == 2):
                        self.form.lblPlaneDefined.setText("Planar motion set to be coincident with a line and point")
                    elif (vertex_counter == 3) and (len(self.ObjectEntities) == 3):
                        self.form.lblPlaneDefined.setText("Planar motion set to be coincident with a set of 3 points")
                    else:
                        self.form.lblPlaneDefined.setText("Planar motion could not be defined from the given entities")
                        FreeCAD.Console.PrintError("\n Plane of motion could not be defined from the given entites \n")
                        FreeCAD.Console.PrintWarning(self.ObjectEntities)
                        FreeCAD.Console.PrintError("\n Select face, 2 lines, line and point or set of three points \n")

        else:
            self.form.stWidg.setCurrentIndex(1)
            self.XVector = self.form.dsbVeci.value()
            self.YVector = self.form.dsbVecj.value()
            self.ZVector = self.form.dsbVeck.value()

            if (self.XVector != 0) or (self.YVector != 0) or (self.ZVector != 0):
                mag = (self.XVector**2 + self.YVector**2 + self.ZVector**2)**0.5
                rounder = 3
                self.obj.UnitVector = FreeCAD.Vector(round(self.XVector/mag, rounder),
                                                    round(self.YVector/mag, rounder),
                                                    round(self.ZVector/mag, rounder))
            else:
                FreeCAD.Console.PrintError("\n Error!!  No Unit Vector has been Defined.  Reverting to:   \n")
                FreeCAD.Console.PrintMessage(self.obj.UnitVector)

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
        self.form.lnedFileDirectory.setText(self.obj.FileDirectory)
        self.form.dsbVeci.setValue(self.obj.XVector)
        self.form.dsbVecj.setValue(self.obj.YVector)
        self.form.dsbVeck.setValue(self.obj.ZVector)
        self.form.lblUnitVecOut.setText(str(self.obj.UnitVector))
        return

    def unitVector(self):
        """ Calculate the unit vector based on user inputs"""
        if self.checkSelectType == 1:
            if (self.XVector != 0) or (self.YVector != 0) or (self.ZVector != 0):
                x_vec = self.XVector
                y_vec = self.YVector
                z_vec = self.ZVector
                mag = (x_vec**2 + y_vec**2 + z_vec**2)**0.5
                i_vec = x_vec/mag
                j_vec = y_vec/mag
                k_vec = z_vec/mag
                unit_vec_unrounded = [i_vec, j_vec, k_vec]
                self.UnitVector = [round(num, 3) for num in unit_vec_unrounded]
                self.form.lblUnitVecOut.setText(self.UnitVector)
        return