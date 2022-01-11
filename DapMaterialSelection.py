 

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
    
    
def makeDapMaterial(name="DapMaterial"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapMaterial(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapJoint(obj.ViewObject)
    return obj


class _CommandDapMaterial:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon5.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Material", "Add New Material Container"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Material", "Add new material container, used to define material properties.")}

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
        import DapMaterialSelection
        DapTools.getActiveAnalysis().addObject(DapMaterialSelection.makeDapMaterial())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Material', _CommandDapMaterial())


class _DapMaterial:
    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "DapMaterial"

        self.initProperties(obj)

    def initProperties(self, obj):
        #addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        #all_subtypes = []
        #for s in DEFINITION_MODES:
            #all_subtypes += s
        #addObjectProperty(obj, 'JointDefinitionMode', all_subtypes, "App::PropertyEnumeration","", "Define how the Joint is defined")
        #addObjectProperty(obj, 'JointType', JOINT_TYPES, "App::PropertyEnumeration", "", "Type of Joint")
        ##addObjectProperty(obj, 'LinkedObjects', [], "App::PropertyLinkList", "", "Linked objects")
        #addObjectProperty(obj, 'DisplayCoordinate', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Vector to display joint visualisation")
        #addObjectProperty(obj, 'Body1', "", "App::PropertyString", "", "Body 1 label")
        #addObjectProperty(obj, 'Body2', "", "App::PropertyString", "", "Body 2 label")
        #addObjectProperty(obj, 'Joint1', "", "App::PropertyString", "", "Joint 1 label")
        #addObjectProperty(obj, 'Joint2', "", "App::PropertyString", "", "Joint 2 label")
        return
        

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
class _ViewProviderDapJoint:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon5.png")
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
        import _TaskPanelDapMaterial
        taskd = _TaskPanelDapMaterial.TaskPanelDapMaterial(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
