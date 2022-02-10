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
# *       Nikra-DAP FreeCAD WorkBench (c) 2022:                                      *
# *         - Please refer to the Documentation and README                           *
# *           for more information regarding this WorkBench and its usage.           *
# *                                                                                  *
# *     Author of this file:                                                         *
# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
# ************************************************************************************

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
                 solver_object,
                 solver_document, 
                 animation_document, 
                 results, 
                 list_of_bodies, 
                 rotation_matrix,
                 Bodies_r,
                 Bodies_p):
        self.obj = solver_object
        self.solver_document = solver_document
        self.animation_document = animation_document
        self.results = np.array(results)
        self.animation_body_objects = FreeCAD.ActiveDocument.Objects
        self.rotation_matrix = rotation_matrix
        self.Bodies_r = Bodies_r
        self.Bodies_p = Bodies_p
        
        self.scale = 1e3 #convert form meters to mm
        
        
        #TODO: link these variables to the properties already defined in dapSolver
        #NOTE: requires the code which is currently still under development
        self.t_initial = self.obj.StartTime
        self.t_final = self.obj.EndTime
        self.reporting_time = self.obj.ReportingTimeStep
        self.folder = self.obj.FileDirectory
        self.plane_norm = self.obj.UnitVector
        self.reportedTimes = self.obj.ReportedTimes

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
        
        self.form.timeStepLabel.setText("{0:5.3f}s / {1:5.3f}s".format(self.t_initial, self.t_final))
            #str(self.t_initial) + "s / " + str(self.t_final) +"s")
        
        #from dapSolver import DapSolver
        
        #TODO creating a new solver instance. Once the DAP solver rewrite has been completed
        #then should just link to the already created instance of the dapsolver
        #self.dapSolver = DapSolver(self.folder)
        
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
        
    def centerOfGravityOfCompound(self, compound):
        #Older versions of FreeCAD does not have centerOfGravity and compound shapes do 
        #not have centerOfMass.
        totVol = 0
        CoG = FreeCAD.Vector(0,0,0)
        for solid in compound.Shape.Solids:
            vol = solid.Volume
            totVol += vol
            CoG += solid.CenterOfMass*vol
        CoG /= totVol
        return CoG

    def moveObjects(self, value):
        #u = self.results[value, :].T
        previous_pos = self.current_pos.copy()
        self.current_pos = self.currentPos(value)
        
        #self.form.timeStepLabel.setText(str(self.reportedTimes[value]) + "s / " + str(self.t_final) +"s")
        self.form.timeStepLabel.setText("{0:5.3f}s / {1:5.3f}s".format(self.reportedTimes[value], self.t_final))
        for bN in range(len(self.list_of_moving_bodies)):
            body_index = self.list_of_bodies.index(self.list_of_moving_bodies[bN])
            
            animation_body_cog = self.centerOfGravityOfCompound(self.animation_body_objects[body_index])
            axis_of_rotation = self.plane_norm

            current_pos = self.current_pos[bN]
            dap_angular_displacement = math.degrees(current_pos[1] - previous_pos[bN][1])
            self.animation_body_objects[body_index].Placement.rotate(animation_body_cog, 
                                                                    axis_of_rotation, 
                                                                    dap_angular_displacement)
            
            #current_pos = self.current_pos[bN]
            dap_pos = FreeCAD.Vector(current_pos[0][0], current_pos[0][1], 0)
            
            rotated_cog = self.centerOfGravityOfCompound(self.animation_body_objects[body_index])
            project_cog = DapTools.projectPointOntoPlane(self.plane_norm, rotated_cog)
            rotated_cog = self.rotation_matrix * project_cog
            
            orthonormal_displacement = dap_pos * self.scale - rotated_cog
            
            required_displacement = self.rotation_matrix.transposed().multVec(orthonormal_displacement)
            
            self.animation_body_objects[body_index].Placement.translate(required_displacement) 
