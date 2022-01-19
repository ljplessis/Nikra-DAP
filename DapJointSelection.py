
#TODO Include license



import FreeCAD
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


JOINT_TYPES = ["Revolute", "Linear Movement"]

DEFINITION_MODES = [["1 Point + 2 Bodies",
                     "alt def mode"], ["2 Points + 2 Bodies"]]

HELPER_TEXT = [["Choose a point and the two bodies attached at the point. Assumes the parts are already correctly \
                 positioned. Useful when assembly is constructed using the Assembly 4 workbench ",
                "Choose a point on each of the two different bodies. The points/faces must belong to each of the \
                 bodies."], ["Choose two points and two bodies, (each point must be attached to its own body)"]]

def makeDapJoints(name="DapJoint"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapJoint(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapJoint(obj.ViewObject)
    return obj


class _CommandDapJoint:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon4.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add New Joint"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add a new joint to the DAP analysis.")}

    def IsActive(self):
        return DapTools.getActiveAnalysis() is not None

    def Activated(self):
        #FreeCAD.ActiveDocument.openTransaction("Create CfdFluidBoundary")
        #FreeCADGui.doCommand("")
        #FreeCADGui.addModule("CfdFluidBoundary")
        #FreeCADGui.addModule("DapTools")
        #FreeCADGui.doCommand("DapTools.getActiveAnalysis().addObject(CfdFluidBoundary.makeCfdFluidBoundary())")
        #FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        import DapTools
        import DapJointSelection
        DapTools.getActiveAnalysis().addObject(DapJointSelection.makeDapJoints())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Joint', _CommandDapJoint())


class _DapJoint:
    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "DapJoint"

        self.initProperties(obj)

    def initProperties(self, obj):
        #addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        all_subtypes = []
        for s in DEFINITION_MODES:
            all_subtypes += s
        addObjectProperty(obj, 'JointDefinitionMode', all_subtypes, "App::PropertyEnumeration","", "Define how the Joint is defined")
        addObjectProperty(obj, 'JointType', JOINT_TYPES, "App::PropertyEnumeration", "", "Type of Joint")
        addObjectProperty(obj, 'DisplayCoordinate', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        addObjectProperty(obj, 'JointCoord1', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        addObjectProperty(obj, 'JointCoord2', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        addObjectProperty(obj, 'Body1', "", "App::PropertyString", "", "Body 1 label")
        addObjectProperty(obj, 'Body2', "", "App::PropertyString", "", "Body 2 label")
        addObjectProperty(obj, 'Joint1', "", "App::PropertyString", "", "Joint 1 label")
        addObjectProperty(obj, 'Joint2', "", "App::PropertyString", "", "Joint 2 label")
        
        

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """
        #TODO should update the representation and scaling of joint visual representation
        r = 10
        shape = Part.makeSphere(r, obj.DisplayCoordinate)
        obj.Shape = shape

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
class _ViewProviderDapJoint:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon4.png")
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

    def onChanged(self, vobj, prop):
        #DapTools.setCompSolid(vobj)
        return

    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    def setEdit(self, vobj, mode):
        import _TaskPanelDapJoint
        taskd = _TaskPanelDapJoint.TaskPanelDapJoint(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
