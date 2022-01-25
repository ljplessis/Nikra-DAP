

#TODO Include license



import FreeCAD
from FreeCAD import Units 
import _FreeCADVectorTools
from _FreeCADVectorTools import dist, normalized, crossproduct,dotproduct, angle, length
import math 
from math import degrees,acos
import os
import DapTools
from DapTools import addObjectProperty
import _BodySelector
from pivy import coin
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


FORCE_TYPES = ["Gravity", "Spring"]

FORCE_TYPE_HELPER_TEXT = ["Universal force of attraction between all matter",
"Spring connecting two points with stiffness and undeformed length"]

# container 
def makeDapForce(name="DapForce"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name) 
    _DapForce(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapForce(obj.ViewObject)
    return obj


class _CommandDapForce:
    """Basic building block of the FreeCAD interface. They appear as a button on the FreeCAD interface, and as a menu entry in menus"""
    
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon6.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Force", "Add Force"),
            """Accel is the shortcut function"""
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Force", "Creates and defines a force for the DAP analysis")}

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not."""
        """If Active AnForce Typesnot FORCE_TYPEStaking place this option will be greyed out"""
        return DapTools.getActiveAnalysis() is not None

    def Activated(self):
        """This function is executed when the workbench is activated"""
        #FreeCAD.ActiveDocument.openTransaction("Create CfdFluidBoundary")
        #FreeCADGui.doCommand("")
        #FreeCADGui.addModule("CfdFluidBoundary")
        #FreeCADGui.addModule("DapTools")
        #FreeCADGui.doCommand("DapTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())")
        #FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        import DapTools
        import DapForceSelection
        DapTools.getActiveAnalysis().addObject(DapForceSelection.makeDapForce())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    """Adding a freecad command """
    FreeCADGui.addCommand('Dap_Force', _CommandDapForce())


class _DapForce:
    def __init__(self, obj):
        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapForce"

        self.bodySelector = _BodySelector.BodySelector

    def initProperties(self, obj):
        addObjectProperty(obj, 'ForceTypes', FORCE_TYPES, "App::PropertyEnumeration", "", "Types of Forces")    
        addObjectProperty(obj, 'gx', "", "App::PropertyAcceleration", "", "X Component")
        addObjectProperty(obj, 'gy', "-9.81 m/s^2", "App::PropertyAcceleration", "", "Y Component")
        addObjectProperty(obj, 'gz', "", "App::PropertyAcceleration", "", "Z Component")
        addObjectProperty(obj, 'Stiffness', "", "App::PropertyQuantity", "", "Stiffness")
        addObjectProperty(obj, 'UndeformedLength', "", "App::PropertyLength", "", "Undeformed Length")
        addObjectProperty(obj, 'Body1', "Randomness", "App::PropertyString", "", "Body 1 label")
        addObjectProperty(obj, 'Body2', "", "App::PropertyString", "", "Body 2 label")
        addObjectProperty(obj, 'Joint1', "", "App::PropertyString", "", "Joint 1 label")
        addObjectProperty(obj, 'Joint2', "", "App::PropertyString", "", "Joint 2 label")
        addObjectProperty(obj, 'JointCoord1', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        addObjectProperty(obj, 'JointCoord2', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        

        obj.Stiffness=Units.Unit('kg/s^2')

        
        
    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create compound part at recompute. """
        return None

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
        

    def onChanged(self, obj, prop):
        if prop == "ForceTypes":
            # FreeCAD.Console.PrintError('This is working')

            if obj.ForceTypes == "Gravity":
                # FreeCAD.Console.PrintError('This is also working')
                obj.setEditorMode("Stiffness", 2)
                obj.setEditorMode("UndeformedLength", 2)
                obj.setEditorMode("Body1", 2)
                obj.setEditorMode("Body2", 2)
                obj.setEditorMode("Joint1", 2)
                obj.setEditorMode("Joint2", 2)
                obj.setEditorMode("gx", 0)
                obj.setEditorMode("gy", 0)
                obj.setEditorMode("gz", 0)
                
            elif obj.ForceTypes == "Spring":
                obj.setEditorMode("gx", 2)
                obj.setEditorMode("gy", 2)
                obj.setEditorMode("gz", 2)
                obj.setEditorMode("Stiffness", 0)
                obj.setEditorMode("UndeformedLength", 0)
                obj.setEditorMode("Body1", 0)
                obj.setEditorMode("Body2", 0)
                obj.setEditorMode("Joint1", 0)
                obj.setEditorMode("Joint2", 0)
                


    
class _ViewProviderDapForce:


    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon6.png")
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
        # TODO choose default display style
        #return "Flat Lines"
        return "Flat Lines"

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
        import _TaskPanelDapForce
        taskd = _TaskPanelDapForce.TaskPanelDapForce(self.Object)
        #for obj in FreeCAD.ActiveDocument.Objects:
            #if obj.isDerivedFrom("Fem::FemMeshObject"):
                #obj.ViewObject.hide()
        #self.Object.ViewObject.show()
        #taskd.obj = vobj.Object
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
