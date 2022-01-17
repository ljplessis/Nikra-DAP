#TODO: add license


class DapWorkbench(Workbench):
    """ Dap workbench option """
    def __init__(self):
        import os
        import DapTools
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon1.png")
        self.__class__.Icon = icon_path
        self.__class__.MenuText = "Nikra-DAP Workbench"
        self.__class__.ToolTip = "Planar multibody dynamics workbench based on Prof. Nikravesh DAP solver"


    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        
        #TODO Add import of all commands here
        from DapAnalysis import _CommandDapAnalysis
        from DapBodySelection import _CommandDapBody
        from DapJointSelection import _CommandDapJoint
        from DapMaterialSelection import _CommandDapMaterial
        from DapSolverRunner import _CommandDapSolver
        
        FreeCADGui.addCommand("Dap_analysis", _CommandDapAnalysis())
        cmdlst = ["Dap_analysis",
                  "Dap_Body",
                  "Dap_Joint",
                  "Dap_Material",
                  "Dap_Solver"]
        
        self.appendToolbar("My Commands",cmdlst) # creates a new toolbar with your commands
        self.appendMenu("Nikra-Dap",cmdlst) # creates a new menu
        #self.appendMenu(["An existing Menu","My submenu"],self.list) # appends a submenu to an existing menu

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
