 




#TODO Include license



import FreeCAD
from FreeCAD import Units 
import os
import os.path
import DapTools
import numpy as np
import sys
import math
from PySide import QtCore


if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    

module_path = DapTools.get_module_path()
sys.path.append(os.path.join(module_path, "dap_solver"))


class TaskPanelAnimate:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, 
                 solver_document, 
                 animation_document, 
                 results, 
                 list_of_bodies, 
                 rotation_matrix,
                 Bodies_r,
                 Bodies_p):
        self.solver_document = solver_document
        self.animation_document = animation_document
        self.results = np.array(results)
        self.animation_body_objects = FreeCAD.ActiveDocument.Objects
        self.rotation_matrix = rotation_matrix
        self.Bodies_r = Bodies_r
        self.Bodies_p = Bodies_p
        

        
        #TODO: link these variables to the properties already defined in dapSolver
        #NOTE: requires the code which is currently still under development
        self.t_initial = 0
        self.t_final = 0.3
        self.reporting_time = 0.01
        self.folder = "/tmp"
        self.plane_norm = FreeCAD.Vector(0,0,1)

        #Should we start of with real speed
        #self.play_back_speed = self.reporting_time*1000 #msec
        self.play_back_speed = 100 #msec
        
        self.n_time_steps = len(self.Bodies_r) - 1

        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.play_back_speed)
        self.timer.timeout.connect(self.onTimerTimeout)
        
        self.list_of_bodies = list_of_bodies
        self.list_of_moving_bodies = DapTools.getListOfMovingBodies(self.list_of_bodies, self.solver_document)

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelAnimate.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        
        self.form.horizontalSlider.setRange(0, self.n_time_steps)
        self.form.horizontalSlider.valueChanged.connect(self.moveObjects)
        
        self.form.startButton.clicked.connect(self.playStart)
        self.form.stopButton.clicked.connect(self.stopStop)
        
        self.form.playSpeed.valueChanged.connect(self.changePlaySpeed)
        
        self.form.timeStepLabel.setText(str(self.t_initial) + "s / " + str(self.t_final) +"s")
        
        from dapSolver import DapSolver
        
        #TODO creating a new solver instance. Once the DAP solver rewrite has been completed
        #then should just link to the already created instance of the dapsolver
        self.dapSolver = DapSolver(self.folder)
        
        #u = self.results[0,:].T
        self.current_pos = self.currentPos(0)


    def currentPos(self, index):
        pos = []
        for bN in range(len(self.Bodies_p[index])):
            dap_pos = self.Bodies_r[index][bN]
            dap_angle = self.Bodies_p[index][bN]
            pos.append([dap_pos, dap_angle])
        return pos

    def reject(self):
        #Closes document and sets the active document back to the solver document
        FreeCADGui.Control.closeDialog()
        FreeCAD.closeDocument(self.animation_document.Name)
        FreeCAD.setActiveDocument(self.solver_document.Name)
        
    def getStandardButtons(self):
        return 0x00200000

    def playStart(self):
        self.timer.start()
    
    def stopStop(self):
        self.timer.stop()
    
    def onTimerTimeout(self):
        tickPosition = self.form.horizontalSlider.value()
        tickPosition += 1
        if tickPosition >= self.n_time_steps:
            if self.form.loopCheckBox.isChecked():
                tickPosition = 0
            else:
                self.timer.stop()
        self.form.horizontalSlider.setValue(tickPosition)

    

    def changePlaySpeed(self, value):
        self.timer.setInterval(self.play_back_speed * (1./value))

    def moveObjects(self, value):
        #u = self.results[value, :].T
        previous_pos = self.current_pos.copy()
        self.current_pos = self.currentPos(value)
        
        self.form.timeStepLabel.setText(str(self.reporting_time * value) + "s / " + str(self.t_final) +"s")
        for bN in range(len(self.list_of_moving_bodies)):
            body_index = self.list_of_bodies.index(self.list_of_moving_bodies[bN])
            animation_body_cog = self.animation_body_objects[body_index].Shape.CenterOfGravity
            axis_of_rotation = self.plane_norm

            current_pos = self.current_pos[bN]
            dap_angular_displacement = math.degrees(current_pos[1] - previous_pos[bN][1])
            self.animation_body_objects[body_index].Placement.rotate(animation_body_cog, 
                                                                    axis_of_rotation, 
                                                                    dap_angular_displacement)
            
            #current_pos = self.current_pos[bN]
            dap_pos = FreeCAD.Vector(current_pos[0][0], current_pos[0][1], 0)
            
            rotated_cog = self.animation_body_objects[body_index].Shape.CenterOfGravity
            project_cog = DapTools.projectPointOntoPlane(self.plane_norm, rotated_cog)
            rotated_cog = self.rotation_matrix * project_cog
            
            orthonormal_displacement = dap_pos - rotated_cog
            
            required_displacement = self.rotation_matrix.transposed().multVec(orthonormal_displacement)
            
            self.animation_body_objects[body_index].Placement.translate(required_displacement) 
