 
 




#TODO Include license



import FreeCAD
from FreeCAD import Units
import os
import os.path
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapBodySelection
import DapSolverBuilder
import numpy as np
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapSolver:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, obj):
        self.obj = obj

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapRunner.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        
        self.form.solveButton.clicked.connect(self.solveButtonClicked)

    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return


    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return True

    def solveButtonClicked(self):
        builder = DapSolverBuilder.DapSolverBuilder()
        #builder.
        builder.t_initial = 0
        builder.t_final = 0.1
        builder.reporting_time = 0.01
        builder.animate = False
        
        
        #TODO: get the save folder from the freecad GUI
        from sys import platform
        if platform == "linux" or platform == "linux2":
            builder.folder = "/tmp/"
        #elif platform == "darwin":
            ## OS X
        elif platform == "win32":
            # Windows...
            builder.folder = "c:\windows\temp"
        
        
        builder.writeBodies()
        builder.writePoints()
        builder.writeJoints()
        builder.writeForces()
        builder.writeFunctions()
        builder.writeUVectors()
        
        FreeCAD.Console.PrintMessage("DAP SOLVER STARTED \n")
        
        builder.solve()
        
        
        builder.loadResults()
        
        Tspan  = np.arange(builder.t_initial, builder.t_final, builder.reporting_time)
        #Tarray = np.zeros( (len(Tspan), len(builder.dapResults)) )
        
        FreeCAD.Console.PrintMessage("Time: " + str(Tspan) + "\n")
        
        nt = len(Tspan)
        
        for i in range(1,nt):
            ##builder.dapResults
            u = builder.dapResults[i,:].T
            
            
            #builder.dapSolver.Update_Position()
            #FreeCAD.Console.PrintMessage("Time " +str(i) + "\n")
            #FreeCAD.Console.PrintMessage("u: " + str(u) + "\n")
            ##u_to_Bodies(u)
            ##Update_Position()
            ##plt.clf()
            ##plot_system() 
            ##plt.pause(pause_time)
        
        #builder.dapSolver
        #FreeCAD.Console.PrintMessage("DAP RESULTS:\n"+str(builder.dapResults)+"\n")
        
        #builder.computeCentreOfGravity()
        
