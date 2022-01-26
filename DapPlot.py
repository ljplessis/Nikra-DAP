 
 
#TODO Add license


import FreeCAD
import DapTools
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    

PLOT_ITEMS = ["Displacement",
              "Velocity",
              "Path Trace",
              "Energy"]

class _CommandDapPlot:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon8.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Plot", "Plot results"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Plot", "Plot results")}

    def IsActive(self):
        return DapTools.getSolverObject().DapResults is not None

    def Activated(self):
        import DapTools
        import DapPlot
        
        
        
        import _TaskPanelPlot
        ##testObject = DapTools.getSolverObject()
        taskd = _TaskPanelPlot.TaskPanelPlot()
        FreeCADGui.Control.showDialog(taskd)



if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Plot', _CommandDapPlot())

