



#TODO Include license




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

        self.default_stiffness = "1 kg/s^2"  
        self.default_length = "1 mm"
        self.default_acceleration = "1 m/s^2"
        self.default_rotstiff = "1 ((kg/s^2)*m)/rad"
        self.default_LinDampCoeff = "1 kg/s"
        self.default_rotDampCoeff = "1 (kg*m)/(s^2*rad)"
        self.default_angle = "1 rad"

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapForces.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.bodySelector = _BodySelector.BodySelector(self.form.bodySelection, self.obj)

        self.form.forceComboBox.addItems(DapForceSelection.FORCE_TYPES)
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = indexOrDefault(DapForceSelection.FORCE_TYPES, self.Type, 0)
        self.form.forceComboBox.setCurrentIndex(bi)

        self.form.forceComboBox.currentIndexChanged.connect(self.comboTypeChanged)

        self.comboTypeChanged()

        self.unitFunc()

        self.rebuildInputs()
    
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

        return 

    def rebuildInputs(self):
    
        setQuantity(self.form.xIn, self.X)
        setQuantity(self.form.yIn, self.Y)
        setQuantity(self.form.zIn, self.Z)
        setQuantity(self.form.stiffnessIn, self.Stiff)
        setQuantity(self.form.undefIn, self.UndefLen)
        setQuantity(self.form.linDampIn,self.LinDampCoeff)
        setQuantity(self.form.rotStiffIn, self.RotStiff)
        setQuantity(self.form.undefAngIn, self.UndefAng)
        setQuantity(self.form.rotDampIn,self.RotDampCoeff)

        # self.Body1 = self.obj.Body1
        # self.Body2 = self.obj.Body2
        # self.Joint1 = self.obj.Joint1
        # self.Joint2 = self.obj.Joint2

    
    def accept(self):
        """If this is missing, there won't be an OK button"""
        
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
        self.obj.Stiffness = getQuantity(self.form.stiffnessIn)
        self.obj.UndeformedLength = getQuantity(self.form.undefIn)
        self.obj.LinDampCoeff = getQuantity(self.form.linDampIn)
        self.obj.RotDampCoeff = getQuantity(self.form.rotDampIn)
        self.obj.RotStiffness = getQuantity(self.form.rotStiffIn)
        self.obj.UndeformedAngle = getQuantity(self.form.undefAngIn)
        
        self.bodySelector.closing()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)        
        self.bodySelector.reject()
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True
    

    def comboTypeChanged(self):
        type_index = self.form.forceComboBox.currentIndex()
        self.form.descriptionhelp.setText(DapForceSelection.FORCE_TYPE_HELPER_TEXT[type_index])
        self.Type = DapForceSelection.FORCE_TYPES[type_index]
        
        
        #self.form.inputForceWidget.setCurrentIndex(type_index)
        
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

