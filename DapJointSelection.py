
#TODO Include license



import FreeCAD
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
import Part
from math import sin, cos, pi

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


JOINT_TYPES = ["Rotation", "Linear Movement"]

DEFINITION_MODES = [["1 Point + 2 Bodies",
                     "alt def mode"], ["2 Points + 2 Bodies"]]

HELPER_TEXT = [["Choose a point and the two bodies attached at the point.",
                "Alternative Deifinition Mode Description"], ["Choose two points and two bodies, (each point must be attached to its own body)"]]

def makeDapJoints(name="DapRelativeMovement"):
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
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add New Relative Movement Between 2 Bodies"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Joint", "Add a new relative movement between two bodies to the DAP analysis.")}

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
        addObjectProperty(obj, 'RelMovDefinitionMode', all_subtypes, "App::PropertyEnumeration","", \
            "Define the relative movement between 2 bodies")
        addObjectProperty(obj, 'TypeOfRelMov', JOINT_TYPES, "App::PropertyEnumeration", "", "Type of Relative Movement")
        addObjectProperty(obj, 'CoordPoint1RelMov', FreeCAD.Vector(0,0,0), "App::PropertyVector", "",\
            "Point 1 used to define relative movement between 2 bodies")
        addObjectProperty(obj, 'CoordPoint2RelMov', FreeCAD.Vector(0,0,0), "App::PropertyVector", "",\
            "Point 2 used to define relative movement between 2 bodies")
        addObjectProperty(obj, 'Body1', "", "App::PropertyString", "", "Label: Body 1")
        addObjectProperty(obj, 'Body2', "", "App::PropertyString", "", "Label: Body 2")
        addObjectProperty(obj, 'Point1RelMov', "", "App::PropertyString", "", "Label: Point 1 of Relative Movement")
        addObjectProperty(obj, 'Point2RelMov', "", "App::PropertyString", "", "Label: Point 2 of Relative Movement")
        
        

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """
        #TODO should update the representation and scaling of based on plane of motion
        #TODO visual representation of the joint should only be vissible if the joint definition mode was correctly specified, e.g. rotation joint needs 1 point AND 2 seperate bodies, translation joint needs 2 points AND 2 bodies

        active_analysis = DapTools.getActiveAnalysis()
        if hasattr(active_analysis, 'Shape'):
            x_lenght = active_analysis.Shape.BoundBox.XLength
            y_lenght = active_analysis.Shape.BoundBox.YLength
            area_dap_analyis_bound_box = x_lenght * y_lenght
            scale_parameter_square_mm = 200000
            scale_factor = area_dap_analyis_bound_box / scale_parameter_square_mm
        else:
            scale_factor = 50

        if obj.TypeOfRelMov == "Rotation":
            r1 = 7*scale_factor
            r2 = scale_factor
            torus_dir = FreeCAD.Vector(0, 0, 1)
            torus = Part.makeTorus(r1, r2, obj.CoordPoint1RelMov, torus_dir, -180, 180, 240)
            cone1_pos = obj.CoordPoint1RelMov + FreeCAD.Vector(r1, -5*r2, 0)
            cone1_dir = FreeCAD.Vector(0, 1, 0)
            cone1 = Part.makeCone(0, 2*r2, 5*r2, cone1_pos, cone1_dir)            
            cone2_pos_x = obj.CoordPoint1RelMov.x -r1*cos(pi/3) + 5*r2*cos(pi/6)
            cone2_pos_y = obj.CoordPoint1RelMov.y -r1*sin(pi/3) - 5*r2*sin(pi/6)
            cone2_pos = FreeCAD.Vector(cone2_pos_x, cone2_pos_y, 0)
            cone2_dir = FreeCAD.Vector(-cos(pi/6), sin(pi/6), 0)
            cone2 = Part.makeCone(0, 2*r2, 5*r2, cone2_pos, cone2_dir)
            torus_w_arrows = Part.makeCompound([torus, cone1, cone2])
            obj.Shape = torus_w_arrows
        elif obj.TypeOfRelMov == "Linear Movement":
            r = scale_factor
            #r = 80
            l = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).Length
            if l > 1e-6:
                lin_move_dir = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).normalize()
                if l > 12*r:
                    cylinder = Part.makeCylinder(r, l - 10*r, obj.CoordPoint1RelMov + 5*r*lin_move_dir, lin_move_dir)
                    cone1 = Part.makeCone(0, 2*r, 5*r, obj.CoordPoint1RelMov, lin_move_dir)
                    cone2 = Part.makeCone(0, 2*r, 5*r, obj.CoordPoint2RelMov, -lin_move_dir)
                else:
                    l = 12*r
                    average_coord = (obj.CoordPoint1RelMov + obj.CoordPoint2RelMov)/2
                    cylinder_pos = average_coord - FreeCAD.Vector(r, 0, 0)
                    cylinder = Part.makeCylinder(r, l - 10*r, cylinder_pos, lin_move_dir)
                    cone1_pos = average_coord - 6*r*lin_move_dir
                    cone2_pos = average_coord + 6*r*lin_move_dir
                    cone1 = Part.makeCone(0, 2*r, 5*r, cone1_pos, lin_move_dir)
                    cone2 = Part.makeCone(0, 2*r, 5*r, cone2_pos, -lin_move_dir)                
                double_arrow = Part.makeCompound([cylinder, cone1, cone2])
                obj.Shape = double_arrow
            else:
                obj.Shape = Part.Shape()

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
