 


#TODO Include license



import FreeCAD
import os
import _FreeCADVectorTools as Vec
import DapTools
from DapTools import addObjectProperty
from pivy import coin
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore

MOTION_PLANES = ["X-Y Plane", 
                 "Y-Z Plane", 
                 "X-Z Plane", 
                 "Custom Plane..."]

MOTION_PLANES_HELPER_TEXT = ["Planar Motion is in XY Plane", 
                             "Planar Motion is in YZ Plane", 
                             "Planar Motion is in XZ Plane", 
                             "User-defined Plane"]

SELECTION_TYPE = ["Normal Vector Definition",
                  "Object Selection", 
                  ]

SELECTION_TYPE_HELPER_TEXT = ["Define the normal vector of the plane of motion",
                              "Experimental: select object entities to define plane of motion. \
Valid selections include a plane, a face or a sketch."
                              ]

def makeDapSolver(name="DapSolver"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapSolver(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapSolver(obj.ViewObject)
    return obj


class _CommandDapSolver:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon7.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Solver", "Run the analysis"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Solver", "Run the analysis.")}

    def IsActive(self):
        return DapTools.getActiveAnalysis() is not None

    def Activated(self):
        import DapTools
        import DapSolverRunner
        solverObject = DapTools.getSolverObject()
        if solverObject == None:
            DapTools.getActiveAnalysis().addObject(DapSolverRunner.makeDapSolver())
            FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        else:
            FreeCADGui.ActiveDocument.setEdit(solverObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Solver', _CommandDapSolver())

class _DapSolver:
    def __init__(self, obj):

        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapSolver"


    def initProperties(self, obj):

        addObjectProperty(obj, 'XVector', 0.0, "App::PropertyFloat","","Vector in X-Direction")
        addObjectProperty(obj, 'YVector', 0.0, "App::PropertyFloat","","Vector in Y-Direction")
        addObjectProperty(obj, 'ZVector', 0.0, "App::PropertyFloat","","Vector in Z-Direction")
        
        addObjectProperty(obj, 'FileDirectory', "", "App::PropertyString", "", "Location where Solver Results will be Stored")
        addObjectProperty(obj, 'MotionPlane', MOTION_PLANES, "App::PropertyEnumeration", "", "Plane of Motion")
        addObjectProperty(obj, 'SelectionType', SELECTION_TYPE, "App::PropertyEnumeration", "", "Type of Custom Plane Selection")
        #addObjectProperty(obj, 'ObjectEntities', [], "App::PropertyStringList","","Objects used for Plane Definition")
        
        
        addObjectProperty(obj, 'PlaneObjectName', "", "App::PropertyString","","Name of object to create custom plane of motion")
        
        addObjectProperty(obj, 'StartTime', 0.0, "App::PropertyFloat","","Start Time")
        addObjectProperty(obj, 'EndTime', 0.5, "App::PropertyFloat","","Start Time")
        addObjectProperty(obj, 'ReportingTimeStep', 0.01, "App::PropertyFloat","","Time intervals for the solution")
        addObjectProperty(obj, "UnitVector", FreeCAD.Vector(0, 0, 0), "App::PropertyVector", "", "Vector Normal to Planar Motion")
        addObjectProperty(obj, 'DapResults', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'ReportedTimes', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_r', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_p', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Points_r', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Points_r_d', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_p_d', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_r_d', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_p_d_d', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'Bodies_r_d_d', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'kinetic_energy', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'potential_energy', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'total_energy', None, "App::PropertyPythonObject", "", "")
        addObjectProperty(obj, 'object_to_point', {}, "App::PropertyPythonObject", "", 
                          "Dictionary linking FC object (eg joint) to DAP point, required for postProcessing")
        addObjectProperty(obj, 'object_to_moving_body', {}, "App::PropertyPythonObject", "", 
                "Dictionary linking FC object to DAP body, required for postProcessing (only moving bodies used)")
        addObjectProperty(obj, 'global_rotation_matrix', FreeCAD.Matrix(), 
                          "App::PropertyMatrix", "", "Global orthonormal rotation matrix")
        return

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """

    def __getstate__(self):
        return None

    def onChanged(self, obj, prop):
        standard_planes = ["X-Y Plane", "Y-Z Plane", "X-Z Plane"]

        if prop == "FileDirectory":
            if obj.FileDirectory == "":
                obj.FileDirectory = os.getcwd()

        if prop == "MotionPlane":
            if obj.MotionPlane in standard_planes:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("SelectionType", 2)
                    obj.setEditorMode("UnitVector", 1)

                if obj.MotionPlane == "X-Y Plane":
                    obj.XVector = 0.0
                    obj.YVector = 0.0
                    obj.ZVector = 1.0

                elif obj.MotionPlane == "Y-Z Plane":
                    obj.XVector = 1.0
                    obj.YVector = 0.0
                    obj.ZVector = 0.0

                else:
                    obj.XVector = 0.0
                    obj.YVector = 1.0
                    obj.ZVector = 0.0

            else:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("SelectionType", 0)
                    obj.setEditorMode("UnitVector", 1)

            if (obj.XVector != 0) or (obj.YVector != 0) or (obj.ZVector != 0):
                mag = (obj.XVector**2 + obj.YVector**2 + obj.ZVector**2)**0.5        
                rounder = 3        
                obj.UnitVector = FreeCAD.Vector(round(obj.XVector/mag, rounder), 
                                                round(obj.YVector/mag, rounder),
                                                round(obj.ZVector/mag, rounder))

        if prop == "SelectionType":
            if obj.SelectionType == "Object Selection":
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("UnitVector", 1)

                #insert code here to determine the positioning of the vector normal to the selection

            else:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 0)
                    obj.setEditorMode("YVector", 0)
                    obj.setEditorMode("ZVector", 0)
                    obj.setEditorMode("UnitVector", 1)
        
        if hasattr(obj, "XVector") and hasattr(obj, "YVector") and hasattr(obj, "ZVector"):
            if prop == "XVector" or prop == "YVector" or prop == "ZVector":

                if (obj.XVector != 0) or (obj.YVector != 0) or (obj.ZVector != 0):
                    mag = (obj.XVector**2 + obj.YVector**2 + obj.ZVector**2)**0.5
                    rounder = 3        
                    obj.UnitVector = FreeCAD.Vector(round(obj.XVector/mag, rounder), 
                                                    round(obj.YVector/mag, rounder),
                                                    round(obj.ZVector/mag, rounder))

    def __setstate__(self, state):
        return None

class _ViewProviderDapSolver:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon7.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard, "Standard")
        #self.ViewObject.Transparency = 95
        return

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        return "Shaded"

    def setDisplayMode(self,mode):
        return mode

    def updateData(self, obj, prop):
        return

    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    def setEdit(self, vobj, mode):
        import _TaskPanelDapSolver
        taskd = _TaskPanelDapSolver.TaskPanelDapSolver(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

