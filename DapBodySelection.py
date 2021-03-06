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
# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              * 
# *        -  Dewald Hattingh (UP) <u17082006@tuks.co.za>                            *
# ************************************************************************************


import FreeCAD

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


BODY_TYPES = ["Ground",
              "Moving"]

BODY_TYPE_HELPER_TEXT = ["A fixed body which does not move.",
                         "A free moving body."]

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
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Body", "Creates and defines a body for the DAP analysis")}

    def IsActive(self):
        return DapTools.getActiveAnalysis() is not None

    def Activated(self):
        import DapTools
        import DapBodySelection
        DapTools.getActiveAnalysis().addObject(DapBodySelection.makeDapBody())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Body', _CommandDapBody())


class _DapBody:
    def __init__(self, obj):
        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapBody"

        

    def initProperties(self, obj):
        addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        addObjectProperty(obj, 'BodyType', BODY_TYPES, "App::PropertyEnumeration", "", "Type of Body")
        addObjectProperty(obj, 'LinkedObjects', [], "App::PropertyLinkList", "", "Linked objects")
        addObjectProperty(obj, 'InitialHorizontal', "", "App::PropertySpeed","","Initial Velocity (Horizontal)")
        addObjectProperty(obj, 'InitialVertical', "", "App::PropertySpeed","","Initial Velocity (Vertical)")
        addObjectProperty(obj, 'InitialAngular', "", "App::PropertyQuantity","","Initial Velocity (Angular)")

        obj.InitialAngular=Units.Unit('rad/s')

    def onDocumentRestored(self, obj):
        self.initProperties(obj)

    def execute(self, obj):
        """ Create compound part at recompute. """
        docName = str(obj.Document.Name)
        doc = FreeCAD.getDocument(docName)
        shape_objects = []
        for i in range(len(obj.References)):
            selection_object = doc.getObjectsByLabel(obj.References[i])[0]
            shape_objects.append(selection_object.Shape)
        shape = Part.makeCompound(shape_objects)
        
        if shape is None:
            obj.Shape = Part.Shape()
        else:
            obj.Shape = shape

    def __getstate__(self):
        return None

    
    def onChanged(self, obj, prop):
        if prop == "BodyType":
            if obj.BodyType == "Ground":

                obj.InitialAngular = "0.0"
                obj.InitialHorizontal = "0.0"
                obj.InitialVertical = "0.0"

                obj.setEditorMode("InitialAngular", 1)
                obj.setEditorMode("InitialHorizontal", 1)
                obj.setEditorMode("InitialVertical", 1)
            else:
                obj.setEditorMode("InitialAngular", 0)
                obj.setEditorMode("InitialHorizontal", 0)
                obj.setEditorMode("InitialVertical", 0)

        #if prop == "References":
            ##Determine if a single body has been referenced under multiple DapBody containers
            #self.lstMultiRef = DapTools.getListOfBodyReferences()
            #self.lstMultiRef_set = set(self.lstMultiRef)
            #self.duplicateRef = len(self.lstMultiRef) != len(self.lstMultiRef_set)
            #if self.duplicateRef == True:
                #FreeCAD.Console.PrintWarning("\n The following elements have been defined under more than one DapBody:  \n")
                #self.lstDuplicateRef = []
                #self.viewed = set()
                #for j in self.lstMultiRef:
                    #if j in self.viewed:
                        #self.lstDuplicateRef.append(j)
                    #else:
                        #self.viewed.add(j)
                ##Provide the user with a list of objects that have been defined multiple times
                #FreeCAD.Console.PrintError(set(self.lstDuplicateRef))
                #FreeCAD.Console.PrintWarning("\n Check for redundant element definitions \n")
            #else:
                #FreeCAD.Console.PrintMessage("\n All DapBody definitions are uniquely defined \n")

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


    def doubleClicked(self, vobj):
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    def setEdit(self, vobj, mode):
        import _TaskPanelDapBody
        taskd = _TaskPanelDapBody.TaskPanelDapBody(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
