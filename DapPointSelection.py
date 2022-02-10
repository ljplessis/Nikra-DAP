# ************************************************************************************
# *                                                                                  *
# *   Copyright (c) 2022 Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>            *
# *   Copyright (c) 2022 Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>   *
# *   Copyright (c) 2022 Dewald Hattingh (UP) <u17082006@tuks.co.za>                 *
# *   Copyright (c) 2022 Varnu Govender (UP) <govender.v@tuks.co.za>                 *
# *                                                                                  *
# *   This program is free software; you can redistribute it and/or modify           *
# *   it under the terms of the GNU Lesser General Public License (LGPL)             *
# *   as published by the Free Software Foundation; either version 2 of              *
# *   the License, or (at your option) any later version.                            *               
# *   for detail see the LICENCE text file.                                          *
# *                                                                                  *
# *   This program is distributed in the hope that it will be useful,                *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of                 *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  *
# *   GNU Library General Public License for more details.                           *
# *                                                                                  *
# *   You should have received a copy of the GNU Library General Public              *   
# *   License along with this program; if not, write to the Free Software            *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307           *
# *   USA                                                                            *
# *_________________________________________________________________________________ *        
# *                                                                                  *
# *     Nikra-DAP FreeCAD WorkBench (c) 2022:                                        *
# *        - Please refer to the Documentation and README                            *
# *          for more information regarding this WorkBench and its usage.            *
# *                                                                                  *
# *     Author(s) of this file:                                                      *                         
# *        -  Varnu Govender (UP) <govender.v@tuks.co.za>                            *
# ************************************************************************************

from lib2to3.pytree import Base
import FreeCAD
from FreeCAD import Units 
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore



# container 
def makeDapPoint(name="DapPoint"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name) 
    _DapPoint(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapForce(obj.ViewObject)
    return obj


class _CommandDapPoint:
    """Basic building block of the FreeCAD interface. They appear as a button on the FreeCAD interface, and as a menu entry in menus"""
    
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon8.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Point", "Add Point"),
            """Accel is the shortcut function"""
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Point", "Creates and defines a point for the DAP analysis")}

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
        import DapPointSelection
        DapTools.getActiveAnalysis().addObject(DapPointSelection.makeDapPoint())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    """Adding a freecad command """
    FreeCADGui.addCommand('Dap_Point', _CommandDapPoint())


class _DapPoint:
    def __init__(self, obj):
        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapPoint"

    def initProperties(self, obj):

        addObjectProperty(obj, 'Point', "", "App::PropertyString", "", "Point label")
        addObjectProperty(obj, 'PointCoord', FreeCAD.Vector(0,0,0), "App::PropertyVector", "", "Point Vector")
        addObjectProperty(obj, 'pointCoordList', [], "App::PropertyVectorList", "", "List of Point Vectors")
        addObjectProperty(obj, 'pointList', [], "App::PropertyStringList", "", "List of Points")
        addObjectProperty(obj, 'bodyNameList', [], "App::PropertyStringList", "", "List of Points")
        addObjectProperty(obj, 'pointAssignList', [], "App::PropertyStringList", "", "List of Points")

        obj.setEditorMode('bodyNameList',2)
        obj.setEditorMode('pointList',2)
        obj.setEditorMode('Point',2)
        obj.setEditorMode('PointCoord',2)


    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create compound part at recompute. """
        shape_list=[]
        r = 0.1 
        if len(obj.pointCoordList)>0:
            for i in range(len(obj.pointList)):
                point = Part.makeSphere(r)
                point.Placement.Base = obj.pointCoordList[i]
                shape_list.append(point)
            shape = Part.makeCompound(shape_list)
            obj.Shape = shape
        else:
            obj.Shape = Part.Shape()
        return None 

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def onChanged(self, obj, prop):
        return None 
 
    
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
        return "Shaded "

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
        import _TaskPanelDapPoint
        taskd = _TaskPanelDapPoint.TaskPanelDapPoint(self.Object)
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
