

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


BODY_TYPES = ["Ground",
              "Moving"]

BODY_TYPE_HELPER_TEXT = ["A fixed body",
                         "A free moving body"]

def makeDapBody(name="DapBody"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapBody(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapBody(obj.ViewObject)
    return obj


class _CommandDapBody:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon3.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Body", "Body Definition"),
            #'Accel': "C, W",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Body", "Creates and defines a body for the DAP analysis")}

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
        import DapBodySelection
        DapTools.getActiveAnalysis().addObject(DapBodySelection.makeDapBody())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Body', _CommandDapBody())


class _DapBody:
    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "DapBody"

        self.initProperties(obj)

    def initProperties(self, obj):
        addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        addObjectProperty(obj, 'BodyType', BODY_TYPES, "App::PropertyEnumeration", "", "Type of Body")
        #addObjectProperty(obj, 'LinkedObjects', [], "App::PropertyLinkList", "", "Linked objects")
        
    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create compound part at recompute. """
        #docName = str(obj.Document.Name)
        #doc = FreeCAD.getDocument(docName)
        #obj.LinkedObjects = []
        #for ref in obj.References:
            #selection_object = doc.getObject(ref[0])
            #if selection_object is not None:  # May have been deleted
                #if selection_object not in obj.LinkedObjects:
                    #obj.LinkedObjects += [selection_object]
        #shape = DapTools.makeShapeFromReferences(obj.References, False)
        #if shape is None:
            #obj.Shape = Part.Shape()
        #else:
            #obj.Shape = shape

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
class _ViewProviderDapBody:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon3.png")
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
        #CfdTools.setCompSolid(vobj)
        return

    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    def setEdit(self, vobj, mode):
        #analysis_object = CfdTools.getParentAnalysisObject(self.Object)
        #if analysis_object is None:
            #CfdTools.cfdError("Boundary must have a parent analysis object")
            #return False
        #physics_model = CfdTools.getPhysicsModel(analysis_object)
        #if not physics_model:
            #CfdTools.cfdError("Analysis object must have a physics object")
            #return False
        #material_objs = CfdTools.getMaterials(analysis_object)

        import _TaskPanelDapBody
        taskd = _TaskPanelDapBody.TaskPanelDapBody(self.Object)
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
