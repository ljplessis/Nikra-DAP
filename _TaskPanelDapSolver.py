 
 




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
import math
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
        current_doc = FreeCADGui.getDocument(self.obj.Document)
        
        body_objects = DapTools.getListOfBodyObjects()
        
        
        
        animation_doc =  FreeCAD.newDocument("Animation")
        animation_doc.copyObject(body_objects)
        FreeCADGui.SendMsgToActiveView("ViewFit")
        animation_body_objects = animation_doc.Objects
        
        
        #for i in range(len(builder.moving_bodies)):
            #body_index = builder.list_of_bodies.index(builder.moving_bodies[i])
            #body_cog = builder.centre_of_gravity_of_body[builder.list_of_bodies[body_index]]
            #axis_of_rotation = builder.plane_norm
            
            
            
            #FreeCAD.Console.PrintMessage("Body index: " +str(body_index) + "\n")
        
        for i in range(1,nt):
            ###builder.dapResults
            u = builder.dapResults[i,:].T
            
            original_pos = []
            for bN in range(len(builder.moving_bodies)):
                dap_pos = builder.dapSolver.Bodies[bN + 1,0].r
                dap_angle = builder.dapSolver.Bodies[bN + 1,0].p
                original_pos.append([dap_pos, dap_angle])
            
            builder.dapSolver.u_to_Bodies(u)
            
            for bN in range(len(builder.moving_bodies)):
                body_index = builder.list_of_bodies.index(builder.moving_bodies[bN])
                
                #body_cog = builder.centre_of_gravity_of_body[builder.list_of_bodies[body_index]]
                
                axis_of_rotation = builder.plane_norm
                animation_body_cog = animation_body_objects[body_index].Shape.CenterOfGravity
                
                #NOTE: TODO dap solver is currently 1 indexing
                dap_pos = builder.dapSolver.Bodies[bN + 1,0].r
                dap_angle = builder.dapSolver.Bodies[bN + 1,0].p
                
                dap_displacement = dap_pos - original_pos[bN][0]
                dap_angular_displacement = math.degrees(dap_angle - original_pos[bN][1])
                
                animation_body_objects[body_index].rotate(animation_body_cog, 
                                                           axis_of_rotation, 
                                                           dap_angular_displacement)
                
                FreeCAD.Console.PrintMessage("Body index: " +str(body_index) + "\n")
                FreeCAD.Console.PrintMessage("Dap Pos: " + str(dap_pos) + "\n")
                FreeCAD.Console.PrintMessage("dap_angle: " + str(dap_angle) + "\n")
                FreeCAD.Console.PrintMessage("dap_angular displacement: " + str(dap_angular_displacement) + "\n")
                FreeCAD.Console.PrintMessage("dap_displacement: " + str(dap_displacement) + "\n")
            
            
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
        
