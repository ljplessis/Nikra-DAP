
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
# ************************************************************************************
import FreeCAD
from FreeCAD import Units
import os
import os.path
import numpy 
import DapTools
from DapTools import indexOrDefault
from DapTools import getQuantity, setQuantity
import DapPointSelection
import _BodySelector 
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    from PySide import QtCore


class TaskPanelDapPoint:
    """ Taskpanel for adding DAP Point """
    

    def __init__(self, obj):
        self.obj = obj
        self.Point = self.obj.Point 
        self.PointCoord = self.obj.PointCoord 
 
        self.doc_name = self.obj.Document.Name

        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapPoint.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.bodySelector = _BodySelector.BodySelector(self.form.bodySelection_1, self.obj)
        
        self.bodySelector.Page3()

        self.rebuildInputs()
        
        return 

    

    def rebuildInputs(self):
        self.Point = self.obj.Point 
        self.PointCoord = self.obj.PointCoord
        
        self.bodySelector.rebuildInputs(2)
        

    def accept(self):
        """If this is missing, there won't be an OK button"""
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.Point = self.Point 
        self.obj.PointCoord = self.PointCoord
        

        self.bodySelector.accept(2)

            
        self.bodySelector.closing()

        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        # self.obj.recompute()
        
        return

    def reject(self):
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        # Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        self.bodySelector.reject()
        self.bodySelector.closing()
        return True
    

  