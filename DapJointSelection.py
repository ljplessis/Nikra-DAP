
#TODO Include license



import FreeCAD
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
from FreeCAD import Units
import Part
from math import sin, cos, pi

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


JOINT_TYPES = ["Rotation", "Linear Movement"]

DEFINITION_MODES = [["1 Point + 2 Bodies",
                     "alt def mode"], ["2 Points + 2 Bodies"]]

HELPER_TEXT = [["Choose a point (by picking an LCS) and the two bodies attached to the point.",\
    "Alternative Deifinition Mode Description"],\
    ["Choose two points (by picking two LCS's) and two bodies, (each point must be attached to its own body)"]]

YES_NO = ["No", "Yes"]

FUNCTION_TYPES = ["Not Applicable", "Function type 'a'", "Function type 'b'", "Function type 'c'"]

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
        addObjectProperty(obj, 'DriverOn', YES_NO, "App::PropertyEnumeration","",\
            "Is a 'driver' switched on to control the defined relative movement?")
        addObjectProperty(obj, 'DriverFunctionType', FUNCTION_TYPES, "App::PropertyEnumeration", "",\
            "Function type that the (switched on) 'driver' will use to control the defined relative movement." )
        addObjectProperty(obj, 'tEndDriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: End time (t_end)")
        addObjectProperty(obj, 'coefC1DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_1'")
        addObjectProperty(obj, 'coefC2DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_2'")
        addObjectProperty(obj, 'coefC3DriverFuncTypeA', "", "App::PropertyQuantity", "",\
            "Driver Function Type A: coefficient 'c_3'")
        addObjectProperty(obj, 'tStartDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: Start time (t_start)")
        addObjectProperty(obj, 'tEndDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: End time (t_end)")
        addObjectProperty(obj, 'initialValueDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: initial function value")
        addObjectProperty(obj, 'endValueDriverFuncTypeB', "", "App::PropertyQuantity", "",\
            "Driver Function Type B: function value at t_end")
        addObjectProperty(obj, 'tStartDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: Start time (t_start)")
        addObjectProperty(obj, 'tEndDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: End time (t_end)")
        addObjectProperty(obj, 'initialValueDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: initial function value")
        addObjectProperty(obj, 'endDerivativeDriverFuncTypeC', "", "App::PropertyQuantity", "",\
            "Driver Function Type C: function derivative at t_end")
        
        obj.tEndDriverFuncTypeA = Units.Unit("")
        obj.coefC1DriverFuncTypeA = Units.Unit("")
        obj.coefC2DriverFuncTypeA = Units.Unit("")
        obj.coefC3DriverFuncTypeA = Units.Unit("")
        
        obj.tStartDriverFuncTypeB = Units.Unit("")
        obj.tEndDriverFuncTypeB = Units.Unit("")
        obj.initialValueDriverFuncTypeB = Units.Unit("")
        obj.endValueDriverFuncTypeB = Units.Unit("")

        obj.tStartDriverFuncTypeC = Units.Unit("")
        obj.tEndDriverFuncTypeC = Units.Unit("")
        obj.initialValueDriverFuncTypeC = Units.Unit("")
        obj.endDerivativeDriverFuncTypeC = Units.Unit("")

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create joint representation part at recompute. """
        #TODO visual representation of the joint should only be vissible if the joint definition mode was correctly specified, e.g. rotation joint needs 1 point AND 2 seperate bodies, translation joint needs 2 points AND 2 bodies
            
        scale_param = 50000

        joint_index = DapTools.indexOrDefault(JOINT_TYPES, obj.TypeOfRelMov, 0)
        
        doc_name = str(obj.Document.Name)
        doc = FreeCAD.getDocument(doc_name)
        
        if joint_index == 0:
            
            body1 = doc.getObjectsByLabel(obj.Body1)
            body2 = doc.getObjectsByLabel(obj.Body2)
                        
            if body1 != [] and body2 != []:
                vol = body1[0].Shape.Volume + body2[0].Shape.Volume
            elif body1 == []:
                vol = body2[0].Shape.Volume
            elif body2 == []:
                vol = body1[0].Shape.Volume
            else:
                vol = 100000
                       
            scale_factor = vol/scale_param                                    
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
            
        elif joint_index == 1:
            l = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).Length
            if l > 1e-6:
                lin_move_dir = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).normalize()
                cylinder = Part.makeCylinder(0.1*l, 0.5*l, obj.CoordPoint1RelMov + 0.25*l*lin_move_dir, lin_move_dir)
                cone1 = Part.makeCone(0, 0.2*l, 0.25*l, obj.CoordPoint1RelMov, lin_move_dir)
                cone2 = Part.makeCone(0, 0.2*l, 0.25*l, obj.CoordPoint2RelMov, -lin_move_dir)
                double_arrow = Part.makeCompound([cylinder, cone1, cone2])
                obj.Shape = double_arrow
            else:
                FreeCAD.Console.PrintError(f"The selected 2 points either coincide, or are too close together!!!")

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
