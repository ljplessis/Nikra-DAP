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
# *     Author(s) of this file:                                                      *
# *        -  Varnu Govender (UP) <govender.v@tuks.co.za>                            *
# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
# ************************************************************************************

from webbrowser import get
import FreeCAD
from FreeCAD import Units
import os
import os.path
import numpy
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapForceSelection
import _BodySelector
import _DapForceDriver
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapForce:
    """ Taskpanel for adding DAP Force """


    def __init__(self, obj):
        self.obj = obj
        self.Type = self.obj.ForceTypes
        self.TypeReset = self.obj.ForceTypes #copy for reset, type gets used a lot

        self.X = self.obj.gx
        self.Y = self.obj.gy
        self.Z = self.obj.gz

        self.Stiff=self.obj.Stiffness
        self.UndefLen=self.obj.UndeformedLength

        self.RotStiff = self.obj.RotStiffness
        self.LinDampCoeff = self.obj.LinDampCoeff
        self.RotDampCoeff = self.obj.RotDampCoeff
        self.UndefAng = self.obj.UndeformedAngle 

        self.Body1 = self.obj.Body1
        self.Body2 = self.obj.Body2
        self.Joint1 = self.obj.Joint1
        self.Joint2 = self.obj.Joint2
        
        self.doc_name = self.obj.Document.Name

        self.default_stiffness = "0 kg/s^2"  
        self.default_length = "0 mm"
        self.default_acceleration = "0 m/s^2"
        self.default_rotstiff = "0 (N*m)/rad"
        self.default_LinDampCoeff = "0 kg/s"
        self.default_rotDampCoeff = "0 (J*s)/rad"
        self.default_angle = "0 rad"

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapForces.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.bodySelector = _BodySelector.BodySelector(self.form.bodySelection, self.obj)
        self.driveSelector = _DapForceDriver.DapForceDriver(self.form.dapForceDriver, self.obj)
        self.form.dapForceDriver.setVisible(False)

        self.form.forceComboBox.addItems(DapForceSelection.FORCE_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapForceSelection.FORCE_TYPES, self.Type, 0)
        self.form.forceComboBox.setCurrentIndex(bi)

        self.form.forceComboBox.currentIndexChanged.connect(self.comboTypeChanged)

        self.form.driveCheck.toggled.connect(self.driveFunc)
        self.form.driveCheck.setEnabled(False)


        self.comboTypeChanged()

        self.unitFunc()

        self.rebuildInputs()

        
        self.form.linDampIn.textChanged.connect(self.dampConCheck)
        self.form.rotDampIn.textChanged.connect(self.dampConCheck)
        self.dampConCheck()

        return 

    def driveFunc(self):
        if self.form.driveCheck.isChecked():
            self.form.dapForceDriver.setVisible(True)
            self.obj.Checker = True

        elif self.form.driveCheck.isChecked() == False:
            self.form.dapForceDriver.setVisible(False) 
            self.obj.Checker = False


    def dampConCheck(self):
        lin = self.form.linDampIn.property("rawValue")
        rot = self.form.rotDampIn.property("rawValue")

        if lin < 0 or rot < 0:
            self.form.dampCon.setText("Undamped")
            self.form.dampCon_2.setText("Undamped")

        elif lin > 1 or rot > 1:
            self.form.dampCon.setText("Overdamped")
            self.form.dampCon_2.setText("Overdamped")

        elif lin == 1 or rot == 1:
            self.form.dampCon.setText("Critically damped")
            self.form.dampCon_2.setText("Crtically damped")

        elif lin < 1 or rot < 1:
            self.form.dampCon.setText("Underdamped")
            self.form.dampCon_2.setText("Underdamped")
            
        return 
    
    def bodySelectionPage(self):

        if self.Type == "Spring" or self.Type == "Linear Spring Damper":
            self.bodySelector.Page1()

        elif self.Type == "Rotational Spring" or self.Type == "Rotational Spring Damper" :
            self.bodySelector.Page2()
        
        else: 
            self.bodySelector.close()

    
    def unitFunc(self):

        acceleration = Units.Quantity(self.default_acceleration)
        length = Units.Quantity(self.default_length)
        stiffness = Units.Quantity(self.default_stiffness)
        rotstiff = Units.Quantity(self.default_rotstiff)
        lindamp = Units.Quantity(self.default_LinDampCoeff)
        rotdamp = Units.Quantity(self.default_rotDampCoeff)
        angle = Units.Quantity(self.default_angle)
        

        setQuantity(self.form.xIn,acceleration)
        setQuantity(self.form.yIn,acceleration)
        setQuantity(self.form.zIn,acceleration)
        setQuantity(self.form.undefIn,length)
        
        setQuantity(self.form.stiffnessIn,stiffness)
        setQuantity(self.form.linDampIn,lindamp)
        setQuantity(self.form.rotStiffIn,rotstiff)
        setQuantity(self.form.undefAngIn,angle)
        setQuantity(self.form.rotDampIn,rotdamp)

        setQuantity(self.form.undefLinIn,length)
        setQuantity(self.form.undefAngRotIn,angle)

        setQuantity(self.form.stiffLinIn,stiffness)
        setQuantity(self.form.stiffRotIn,rotstiff)
        return 

    def rebuildInputs(self):
    
        setQuantity(self.form.xIn, self.X)
        setQuantity(self.form.yIn, self.Y)
        setQuantity(self.form.zIn, self.Z)
        
        setQuantity(self.form.linDampIn,self.LinDampCoeff)
        
        setQuantity(self.form.rotDampIn,self.RotDampCoeff)

        if self.obj.ForceTypes == "Spring":
            setQuantity(self.form.undefIn, self.UndefLen)
            setQuantity(self.form.stiffnessIn, self.Stiff)
        elif self.obj.ForceTypes == "Linear Spring Damper":
            setQuantity(self.form.undefLinIn,self.UndefLen)
            setQuantity(self.form.stiffLinIn, self.Stiff)
        if self.obj.ForceTypes == "Rotational Spring":
            setQuantity(self.form.undefAngIn, self.UndefAng)
            setQuantity(self.form.rotStiffIn, self.RotStiff)
        elif self.obj.ForceTypes == "Rotational Spring Damper":
            setQuantity(self.form.undefAngRotIn,self.UndefAng)
            setQuantity(self.form.stiffRotIn, self.RotStiff)
        
        if self.obj.Checker:
            self.form.driveCheck.setChecked(True)

    
    def accept(self):
        """If this is missing, there won't be an OK button"""
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        
        if self.Type == 'Gravity' and  DapTools.gravityChecker():
            FreeCAD.Console.PrintError('Gravity has already been selected')
        
        if self.Type == "Spring" or self.Type == "Linear Spring Damper":
            self.bodySelector.accept(0)
            #self.bodySelector.execute(self.obj,0)
        elif self.Type == "Rotational Spring" or self.Type == "Rotational Spring Damper":
            self.bodySelector.accept(1)
            #self.bodySelector.execute(self.obj,1)
        
        self.obj.ForceTypes = self.Type
        self.obj.gx = getQuantity(self.form.xIn)
        self.obj.gy = getQuantity(self.form.yIn)
        self.obj.gz = getQuantity(self.form.zIn)

        self.obj.LinDampCoeff = getQuantity(self.form.linDampIn)
        self.obj.RotDampCoeff = getQuantity(self.form.rotDampIn)
        

        if self.obj.ForceTypes == "Spring":
            self.obj.UndeformedLength = getQuantity(self.form.undefIn)
            self.obj.Stiffness = getQuantity(self.form.stiffnessIn)
        elif self.obj.ForceTypes == "Linear Spring Damper":
            self.obj.UndeformedLength = getQuantity(self.form.undefLinIn)
            self.obj.Stiffness = getQuantity(self.form.stiffLinIn)
            

        if self.obj.ForceTypes == "Rotational Spring":
            self.obj.UndeformedAngle = getQuantity(self.form.undefAngIn)
            self.obj.RotStiffness = getQuantity(self.form.rotStiffIn)

        elif self.obj.ForceTypes == "Rotational Spring Damper":
            self.obj.UndeformedAngle = getQuantity(self.form.undefAngRotIn)
            self.obj.RotStiffness = getQuantity(self.form.stiffRotIn)
            
        self.driveSelector.accept()
        self.bodySelector.closing()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        
        ##Do the reject checker before resetting the force type to previous selection
        if self.obj.ForceTypes == "Spring" or self.obj.ForceTypes == "Linear Spring Damper":
            self.bodySelector.reject(0)
            ##self.bodySelector.execute(self.obj,0)
        elif self.obj.ForceTypes == "Rotational Spring" or self.obj.ForceTypes == "Rotational Spring Damper":
            self.bodySelector.reject(1)
        
        
        self.obj.ForceTypes = self.TypeReset
        
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)        
        #self.bodySelector.reject()
        #FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        self.obj.recompute()
        return True
    

    def comboTypeChanged(self):
        type_index = self.form.forceComboBox.currentIndex()
        self.form.descriptionhelp.setText(DapForceSelection.FORCE_TYPE_HELPER_TEXT[type_index])
        self.Type = DapForceSelection.FORCE_TYPES[type_index]
        
        #TODO reset type on reject
        self.obj.ForceTypes = self.Type

        if self.Type == "Gravity":
            self.form.driveCheck.setChecked(False)
            self.form.driveCheck.setVisible(False)
        else:
            self.form.driveCheck.setVisible(True)
        
        
        self.form.inputForceWidget.setCurrentIndex(type_index)
        
        self.obj.recompute()

        if self.Type == "Spring" or self.Type == "Linear Spring Damper":
            self.form.bodySelection.setVisible(True)
            self.bodySelector.Page1()

        elif self.Type == "Rotational Spring" or self.Type == "Rotational Spring Damper" :
            self.form.bodySelection.setVisible(True)
            self.bodySelector.Page2()
        
        #elif self.Type == "Gravity":
            #self.bodySelector.close()
        else:
            self.form.bodySelection.setVisible(False)

