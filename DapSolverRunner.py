 


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

        obj.Proxy = self
        self.Type = "DapSolver"

        self.initProperties(obj)

    def initProperties(self, obj):
        addObjectProperty(obj, 'DapResults', None, "App::PropertyPythonObject", "", "")
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
        addObjectProperty(obj, 'global_rotation_matrix', FreeCAD.Matrix(), "App::PropertyMatrix", "", "Global orthonormal rotation matrix")
        #addObjectProperty(obj, 'MaterialDictionary', {}, "App::PropertyPythonObject", "", "Dictionary of parts and linked material properties")
        return
        

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """

    def __getstate__(self):
        return None

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
