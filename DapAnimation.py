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
    


class _CommandDapAnimation:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon8.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Animation", "Animate solution"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Animation", "Animates the motion of the moving bodies")}

    def IsActive(self):
        return DapTools.getSolverObject().DapResults is not None

    def Activated(self):
        import DapTools
        import DapAnimation
        
        solver_doc = FreeCAD.ActiveDocument
        
        docName = "Animation"
        body_objects = DapTools.getListOfBodyObjects()
        solver_object = DapTools.getSolverObject()
        results = solver_object.DapResults
        rotation_matrix = solver_object.global_rotation_matrix
        Bodies_r = solver_object.Bodies_r
        Bodies_p = solver_object.Bodies_p
        
        if docName in FreeCAD.listDocuments():
            FreeCAD.setActiveDocument(docName)
        else:
            FreeCAD.newDocument(docName)
        animation_doc = FreeCAD.ActiveDocument


        

        list_of_bodies = []
        for body in body_objects:
            a = animation_doc.addObject("Part::Feature", body.Label)
            #FreeCAD.Console.PrintMessage("In animate body.label: ")
            animation_doc.getObject(a.Name).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)
        
        FreeCADGui.SendMsgToActiveView("ViewFit")
        
        
        
        import _TaskPanelAnimate
        taskd = _TaskPanelAnimate.TaskPanelAnimate(solver_object,
                                                   solver_doc,
                                                   animation_doc,
                                                   results,
                                                   list_of_bodies,
                                                   rotation_matrix,
                                                   Bodies_r,
                                                   Bodies_p)
        FreeCADGui.Control.showDialog(taskd)



if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Animation', _CommandDapAnimation())

