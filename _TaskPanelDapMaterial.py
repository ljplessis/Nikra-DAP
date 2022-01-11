 




#TODO Include license



import FreeCAD
import os
import os.path
import DapTools
from DapTools import indexOrDefault
import DapBodySelection
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    
class TaskPanelDapMaterial:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, obj):
        self.obj = obj
        self.doc_name = self.obj.Document.Name
        
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapMaterials.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.body_labels = DapTools.getListOfBodyLabels()
        self.form.bodyCombo.addItems(self.body_labels)
        
        self.form.bodyCombo.currentIndexChanged.connect(self.bodyComboSelectionChanged)
        #FreeCAD.Console.PrintMessage(self.body_labels)
        
        
        
    def accept(self):
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return
    
    
    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True
    
    def bodyComboSelectionChanged(self):
        ci = self.form.bodyCombo.currentIndex()
        #body_object = FreeCAD.get
        #FreeCAD.Console.PrintMessage(self.body_labels[ci])
        
        
        #The following snippet of code comes from MaterialEditor.py by Yorik van Havre, Bernd Hahnebach
        from materialtools.cardutils import import_materials as getmats
        self.materials, self.cards, self.icons = getmats()

        card_name_list = []  # [ [card_name, card_path, icon_path], ... ]

        for a_path in sorted(self.materials.keys()):
                card_name_list.append([self.cards[a_path], a_path, self.icons[a_path]])
                FreeCAD.Console.PrintMessage(self.cards[a_path])
                FreeCAD.Console.PrintMessage("\n")
        card_name_list.insert(0, ["Manual definition", "", ""])
        #if sort_by_resources is True:
            #for a_path in sorted(self.materials.keys()):
                #card_name_list.append([self.cards[a_path], a_path, self.icons[a_path]])
        #else:
            #card_names_tmp = {}
            #for path, name in self.cards.items():
                #card_names_tmp[name] = path
            #for a_name in sorted(card_names_tmp.keys()):
                #a_path = card_names_tmp[a_name]
                #card_name_list.append([a_name, a_path, self.icons[a_path]])

        
        
        
        
        
        
        
        
        
        
        docName = str(self.doc_name)
        doc = FreeCAD.getDocument(docName)
        self.form.tableWidget.clearContents()
        self.form.tableWidget.setRowCount(0)
        self.form.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        
        
        selection_object = doc.getObjectsByLabel(self.body_labels[ci])[0]
        list_of_parts = selection_object.References
        #for part in list_of_parts:
        for i in range(len(list_of_parts)):
            self.form.tableWidget.insertRow(i)
            combo = QtGui.QComboBox()
            
            for mat in card_name_list:
                combo.addItem(QtGui.QIcon(mat[2]), mat[0], mat[1])
            
            partName = QtGui.QTableWidgetItem(str(list_of_parts[i]))
            #density = 
            self.form.tableWidget.setItem(i,0,partName)
            self.form.tableWidget.setCellWidget(i,1,combo)
            
            #combo.
            
            
        
        
        ##self.form.listWidget.insertItem(0,combo)
        ###FreeCAD.Console.PrintMessage(selection_object)
        ##FreeCAD.Console.PrintMessage(selection_object.References)
        
