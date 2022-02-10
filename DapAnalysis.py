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
# ************************************************************************************

import FreeCAD

import FreeCAD
import DapTools
from DapTools import addObjectProperty
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore


def makeDapAnalysis(name):
    """ Create Dap Analysis group object """
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    _DapAnalysis(obj)

    if FreeCAD.GuiUp:
        _ViewProviderDapAnalysis(obj.ViewObject)
    return obj

class _DapAnalysis:
    """ The Dap analysis group """
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "DapAnalysis"
        self.initProperties(obj)

    def initProperties(self, obj):
        #obj.addProperty("App::PropertyPath","OutputPath")
        addObjectProperty(obj, "OutputPath", "", "App::PropertyPath", "",
                          "Path to which cases are written (blank to use system default)")
        addObjectProperty(obj, "IsActiveAnalysis", False, "App::PropertyBool", "", "Active analysis object in document")
        obj.setEditorMode("IsActiveAnalysis", 1)  # Make read-only (2 = hidden)

    def onDocumenRestored(self, obj):
        self.initProperties(obj)

class _CommandDapAnalysis:
    """ The Dap Analysis command definition """
    def __init__(self):
        pass

    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon2.png")
        return {'Pixmap': icon_path,
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_analysis", "New Dap Analysis"),
                'Accel': "N, C",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_analysis", 
                                                    "Creates a Dap solver container.")}

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


    def Activated(self):
        #This is an example of how to allow for macro recording
        FreeCAD.ActiveDocument.openTransaction("Create Dap Analysis")
        FreeCADGui.doCommand("")
        #import DapAnalysis
        #import DapTools
        #analysis = DapAnalysis.makeDapAnalysis("DapAnalysis")
        FreeCADGui.addModule("DapAnalysis")
        FreeCADGui.addModule("DapTools")
        FreeCADGui.doCommand("analysis = DapAnalysis.makeDapAnalysis('DapAnalysis')")
        FreeCADGui.doCommand("DapTools.setActiveAnalysis(analysis)")

        #TODO add any other object creations that should happen by default when
        # the workbench is initialised here


class _ViewProviderDapAnalysis:
    """ A view provider for the DapAnalysis container object """
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon2.png")
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.bubbles = None

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def doubleClicked(self, vobj):
        if not DapTools.getActiveAnalysis() == self.Object:
            if FreeCADGui.activeWorkbench().name() != 'DapWorkbench':
                FreeCADGui.activateWorkbench("DapWorkbench")
            DapTools.setActiveAnalysis(self.Object)
            return True
        return True

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

