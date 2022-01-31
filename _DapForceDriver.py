from pickle import FALSE
import FreeCAD
from FreeCAD import Units 
import os
import os.path
import DapTools 
from DapTools import indexOrDefault
from DapTools import addObjectProperty
from DapTools import getQuantity, setQuantity 
import DapForceSelection
import _TaskPanelDapForce
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide import QtCore
    from PySide import QtGui
    from PySide.QtCore import QTimer
    import PySide
import Part

class DapForceDriver:
    def __init__(self,parent_widget, obj):
        ui_path = os.path.join(os.path.dirname(__file__), "DapForceDriver.ui")
        self.parent_widget = parent_widget
        self.form = FreeCADGui.PySideUic.loadUi(ui_path, self.parent_widget)
        self.parent_widget.layout().addWidget(self.form)

        self.obj = obj 
        self.doc_name = self.obj.Document.Name
        self.view_object = self.obj.ViewObject
        self.emptyunit = ""

        self.form.radtype_a.toggled.connect(lambda: self.funcChanged(0))
        self.form.radtype_b.toggled.connect(lambda: self.funcChanged(1))
        self.form.radtype_c.toggled.connect(lambda: self.funcChanged(2))

        self.unitFunc()
        
        self.rebuildInputs()
    
    
    def accept(self):

        if self.form.radtype_a.isChecked():
            self.obj.a_Checker = True 
            self.obj.b_Checker = False 
            self.obj.c_Checker = False

            self.obj.tEndDriverFuncTypeA = getQuantity(self.form.tEndFuncA)
            self.obj.coefC1DriverFuncTypeA = getQuantity(self.form.FuncACoefC1)
            self.obj.coefC2DriverFuncTypeA = getQuantity(self.form.FuncACoefC2)
            self.obj.coefC3DriverFuncTypeA = getQuantity(self.form.FuncACoefC3)

            
            setQuantity(self.form.tStartFuncB, 0.0)
            setQuantity(self.form.tEndFuncB, 0.0)
            setQuantity(self.form.startValueFuncB, 0.0)
            setQuantity(self.form.endValueFuncB, 0.0)

            setQuantity(self.form.tStartFuncC, 0.0)
            setQuantity(self.form.tEndFuncC, 0.0)
            setQuantity(self.form.startValueFuncC, 0.0)
            setQuantity(self.form.endDerivativeFuncC, 0.0)


        if self.form.radtype_b.isChecked():
            self.obj.b_Checker = True
            self.obj.a_Checker = False 
            self.obj.c_Checker = False

            self.obj.tStartDriverFuncTypeB = getQuantity(self.form.tStartFuncB)
            self.obj.tEndDriverFuncTypeB = getQuantity(self.form.tEndFuncB)
            self.obj.initialValueDriverFuncTypeB = getQuantity(self.form.startValueFuncB)
            self.obj.endValueDriverFuncTypeB = getQuantity(self.form.endValueFuncB)  

                
            
            setQuantity(self.form.tEndFuncA, 0.0)
            setQuantity(self.form.FuncACoefC1, 0.0)
            setQuantity(self.form.FuncACoefC2, 0.0)
            setQuantity(self.form.FuncACoefC3, 0.0)

                
            setQuantity(self.form.tStartFuncC, 0.0)
            setQuantity(self.form.tEndFuncC, 0.0)
            setQuantity(self.form.startValueFuncC, 0.0)
            setQuantity(self.form.endDerivativeFuncC, 0.0)


        if self.form.radtype_c.isChecked():
            self.obj.c_Checker = True
            self.obj.a_Checker = False 
            self.obj.b_Checker = False  
                
            self.obj.tStartDriverFuncTypeC = getQuantity(self.form.tStartFuncC)
            self.obj.tEndDriverFuncTypeC = getQuantity(self.form.tEndFuncC)
            self.obj.initialValueDriverFuncTypeC = getQuantity(self.form.startValueFuncC)
            self.obj.endDerivativeDriverFuncTypeC = getQuantity(self.form.endDerivativeFuncC)

    
            setQuantity(self.form.tEndFuncA, 0.0)
            setQuantity(self.form.FuncACoefC1, 0.0)
            setQuantity(self.form.FuncACoefC2, 0.0)
            setQuantity(self.form.FuncACoefC3, 0.0)

            setQuantity(self.form.tStartFuncB, 0.0)
            setQuantity(self.form.tEndFuncB, 0.0)
            setQuantity(self.form.startValueFuncB, 0.0)
            setQuantity(self.form.endValueFuncB, 0.0)



        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return


    def unitFunc(self):

        emptyunit = Units.Quantity(self.emptyunit)
        setQuantity(self.form.tEndFuncA, emptyunit)
        setQuantity(self.form.FuncACoefC1, emptyunit)
        setQuantity(self.form.FuncACoefC2, emptyunit)
        setQuantity(self.form.FuncACoefC3, emptyunit)

        setQuantity(self.form.tStartFuncB, emptyunit)
        setQuantity(self.form.tEndFuncB, emptyunit)
        setQuantity(self.form.startValueFuncB, emptyunit)
        setQuantity(self.form.endValueFuncB, emptyunit)

        setQuantity(self.form.tStartFuncC, emptyunit)
        setQuantity(self.form.tEndFuncC, emptyunit)
        setQuantity(self.form.startValueFuncC, emptyunit)
        setQuantity(self.form.endDerivativeFuncC, emptyunit)

        return 


    def rebuildInputs(self):
        setQuantity(self.form.tEndFuncA, self.obj.tEndDriverFuncTypeA)
        setQuantity(self.form.FuncACoefC1, self.obj.coefC1DriverFuncTypeA)
        setQuantity(self.form.FuncACoefC2, self.obj.coefC2DriverFuncTypeA)
        setQuantity(self.form.FuncACoefC3, self.obj.coefC3DriverFuncTypeA)

        setQuantity(self.form.tStartFuncB, self.obj.tStartDriverFuncTypeB)
        setQuantity(self.form.tEndFuncB, self.obj.tEndDriverFuncTypeB)
        setQuantity(self.form.startValueFuncB, self.obj.initialValueDriverFuncTypeB)
        setQuantity(self.form.endValueFuncB, self.obj.endValueDriverFuncTypeB)

        setQuantity(self.form.tStartFuncC, self.obj.tStartDriverFuncTypeC)
        setQuantity(self.form.tEndFuncC, self.obj.tEndDriverFuncTypeC)
        setQuantity(self.form.startValueFuncC, self.obj.initialValueDriverFuncTypeC)
        setQuantity(self.form.endDerivativeFuncC, self.obj.endDerivativeDriverFuncTypeC)

        if self.obj.a_Checker:
            self.form.radtype_a.setChecked(True)
        if self.obj.b_Checker:
            self.form.radtype_b.setChecked(True)
        if self.obj.c_Checker:
            self.form.radtype_c.setChecked(True)

    
    def funcChanged(self,index):
        self.form.typeInput.setCurrentIndex(index+1)

    # def propertyEditor(self):


    

        


