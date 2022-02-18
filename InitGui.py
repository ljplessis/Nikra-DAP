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

class DapWorkbench(Workbench):
    """ Dap workbench option """
    def __init__(self):
        import os
        import DapTools
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon1.png")
        self.__class__.Icon = icon_path
        self.__class__.MenuText = "Nikra-DAP"
        self.__class__.ToolTip = "Planar multibody dynamics workbench based on Prof. Nikravesh DAP solver"


    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        
        #TODO Add import of all commands here
        from DapAnalysis import _CommandDapAnalysis
        from DapBodySelection import _CommandDapBody
        from DapJointSelection import _CommandDapJoint
        from DapForceSelection import _CommandDapForce
        from DapMaterialSelection import _CommandDapMaterial
        from DapSolverRunner import _CommandDapSolver
        from DapAnimation import _CommandDapAnimation
        from DapPlot import _CommandDapPlot
        from DapPointSelection import _CommandDapPoint
        
        FreeCADGui.addCommand("Dap_analysis", _CommandDapAnalysis())
        cmdlst = ["Dap_analysis",
                  "Separator",
                  "Dap_Body",
                  "Dap_Joint",
                  "Dap_Material",
                  "Dap_Force",
                  #"Dap_Point",#point functionality has not yet been included in the solver builder
                  "Separator",
                  "Dap_Solver",
                  "Separator",
                  "Dap_Animation",
                  "Dap_Plot",
                  
                  ]
                  #"Dap_Point"]
        
        self.appendToolbar("My Commands",cmdlst) # creates a new toolbar with your commands
        self.appendMenu("Nikra-Dap",cmdlst) # creates a new menu

    def Activated(self):
        """This function is executed when the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        #self.appendContextMenu("My commands",cmdlst) # add commands to the context menu

    def GetClassName(self): 
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"
       
Gui.addWorkbench(DapWorkbench()) 
