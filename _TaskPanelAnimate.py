 




#TODO Include license



import FreeCAD
from FreeCAD import Units 
import os
import os.path
import DapTools
import numpy as np
import sys
import math

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    

module_path = DapTools.get_module_path()
sys.path.append(os.path.join(module_path, "dap_solver"))


class TaskPanelAnimate:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, solver_document, animation_document, results, list_of_bodies, rotation_matrix):
        self.solver_document = solver_document
        self.animation_document = animation_document
        self.results = np.array(results)
        self.animation_body_objects = FreeCAD.ActiveDocument.Objects
        self.rotation_matrix = rotation_matrix
        
        #TODO: link these variables to the properties already defined in dapSolver
        #NOTE: requires the code which is currently still under development
        self.t_initial = 0
        self.t_final = 0.3
        self.reporting_time = 0.01
        self.folder = "/tmp"
        self.plane_norm = FreeCAD.Vector(0,0,1)
        #builder.animate = False
        
        self.list_of_bodies = list_of_bodies
        self.list_of_moving_bodies = DapTools.getListOfMovingBodies(self.list_of_bodies, self.solver_document)
        FreeCAD.Console.PrintMessage("list of moving bodies: " + str(self.list_of_moving_bodies) + "\n")
        
        #FreeCAD.Console.PrintMessage("Results: " + str(self.results) + "\n")
        #FreeCAD.Console.PrintMessage("Results shape 0: " + str(self.results.shape[0]) + "\n")
        #FreeCAD.Console.PrintMessage("Results shape 1: " + str(self.results.shape[1]) + "\n")
    
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelAnimate.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        
        self.form.horizontalSlider.setRange(0, self.results.shape[0]-1)
        self.form.horizontalSlider.valueChanged.connect(self.sliderMoved)
        
         
        
        from dapSolver import DapSolver
        
        #TODO creating a new solver instance. Once the DAP solver rewrite has been completed
        #then should just link to the already created instance of the dapsolver
        self.dapSolver = DapSolver(self.folder)
        
        u = self.results[0,:].T
        self.current_pos = self.currentPos(u)
        #self.
        
        
        #self.builder = DapSolverBuilder.DapSolverBuilder(self.obj)
        ##builder.
        #self.builder.t_initial = 0
        #self.builder.t_final = 0.3
        #self.builder.reporting_time = 0.01
        #self.builder.animate = False

    def currentPos(self, u):
        self.dapSolver.u_to_Bodies(u)
        #self.current_pos = 
        #self.original_pos = []
        pos = []
        #NOTE: dap solver is currently 1 indexing.
        for bN in range(1,self.dapSolver.nB):
            dap_pos = self.dapSolver.Bodies[bN,0].r
            dap_angle = self.dapSolver.Bodies[bN,0].p
            pos.append([dap_pos, dap_angle])
        return pos

    def reject(self):
        FreeCAD.Console.PrintMessage("Successfully called on close \n")
        FreeCADGui.Control.closeDialog()
        FreeCAD.closeDocument(self.animation_document.Name)
        FreeCAD.setActiveDocument(self.solver_document.Name)
        #FreeCAD.ActiveDocument.resetEdit()
        
    def getStandardButtons(self):
        return 0x00200000

    def sliderMoved(self, value):
        u = self.results[value, :].T
        #self.dapSolver.u_to_Bodies(u)
        previous_pos = self.current_pos.copy()
        self.current_pos = self.currentPos(u)
        for bN in range(len(previous_pos)):
            body_index = self.list_of_bodies.index(self.list_of_moving_bodies[bN])
            animation_body_cog = self.animation_body_objects[body_index].Shape.CenterOfGravity
            axis_of_rotation = self.plane_norm
            #animation_body_cog = 
            dap_angular_displacement = math.degrees(self.current_pos[bN][1] - previous_pos[bN][1])
            self.animation_body_objects[body_index].Placement.rotate(animation_body_cog, 
                                                                    axis_of_rotation, 
                                                                    dap_angular_displacement)
            
            dap_pos = self.current_pos[bN][0]
            dap_pos = FreeCAD.Vector(dap_pos[0], dap_pos[1], 0)
            
            rotated_cog = self.animation_body_objects[body_index].Shape.CenterOfGravity
            project_cog = DapTools.projectPointOntoPlane(self.plane_norm, rotated_cog)
            rotated_cog = self.rotation_matrix * project_cog
            
            orthonormal_displacement = dap_pos - rotated_cog
            
            required_displacement = self.rotation_matrix.transposed().multVec(orthonormal_displacement)
            
            self.animation_body_objects[body_index].Placement.translate(required_displacement) 
            #FreeCAD.Console.PrintMessage(i)
        #for i 
        FreeCAD.Console.PrintMessage("Current slider position: " + str(value) + "\n")
