 




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
    from PySide import QtCore
    
class TaskPanelDapMaterial:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self, obj):
        self.obj = obj
        self.MaterialDictionary = self.obj.MaterialDictionary
        
        self.default_density = "1 kg/m^3"
        
        self.fetchFreeCADMaterials()
        
        self.doc_name = self.obj.Document.Name
        
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapMaterials.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        self.body_labels = DapTools.getListOfBodyLabels()
        self.form.bodyCombo.addItems(self.body_labels)
        
        self.form.bodyCombo.currentIndexChanged.connect(self.bodyComboSelectionChanged)
        self.bodyComboSelectionChanged()

        self.form.tableWidget.cellClicked.connect(self.tableWidgetCellClicked)


    def accept(self):
        self.obj.MaterialDictionary = self.MaterialDictionary
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return


    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        #FreeCAD.getDocument(doc_name).recompute()
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return True

    def fetchFreeCADMaterials(self):
        # Prepulate list of available material properties in FreeCAD
        # The following snippet of code comes from MaterialEditor.py by Yorik van Havre, Bernd Hahnebach
        from materialtools.cardutils import import_materials as getmats
        self.materials, self.cards, self.icons = getmats()

        self.card_name_list = []  # [ [card_name, card_path, icon_path], ... ]
        self.card_name_labels = []

        for a_path in sorted(self.materials.keys()):
                self.card_name_list.append([self.cards[a_path], a_path, self.icons[a_path]])
                self.card_name_labels.append(self.cards[a_path])
        self.card_name_list.insert(0, ["Manual Definition", "", ""])
        self.card_name_labels.insert(0,"Manual Definition")


    def bodyComboSelectionChanged(self):
        ci = self.form.bodyCombo.currentIndex()

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

            for mat in self.card_name_list:
                combo.addItem(QtGui.QIcon(mat[2]), mat[0], mat[1])

            current_body_label = list_of_parts[i]
            
            partName = QtGui.QTableWidgetItem(current_body_label)
            partName.setFlags(QtCore.Qt.ItemIsEnabled)
            self.form.tableWidget.setItem(i,0,partName)
            self.form.tableWidget.setCellWidget(i,1,combo)
            
            if current_body_label in self.MaterialDictionary.keys():
                mat_name = self.MaterialDictionary[current_body_label]["matName"]
                mi = indexOrDefault(self.card_name_labels, mat_name, 0)
                combo.setCurrentIndex(mi)
                self.setDensityInTable(mi, i)

            combo.currentIndexChanged.connect(self.materialComboChanged)


    def materialComboChanged(self, index):
        current_row = self.form.tableWidget.currentRow()
        self.setDensityInTable(index, current_row)


    def setDensityInTable(self, index, current_row):
        current_mat_choice = self.card_name_list[index]
        part_label = self.form.tableWidget.item(current_row, 0).text()
        #index 0 is manual editing
        if index == 0:
            density = self.default_density
            density_item = QtGui.QTableWidgetItem(density)
        else:
            density = self.materials[current_mat_choice[1]]["Density"]
            density_item = QtGui.QTableWidgetItem(str(density))
            density_item.setFlags(QtCore.Qt.ItemIsEnabled)

        self.form.tableWidget.setItem(current_row, 2, density_item)

        self.MaterialDictionary[part_label] = {"matName": current_mat_choice[0],
                                               "density" : density}

    def tableWidgetCellClicked(self, row, column):
        # select the object to make it visible
        if column == 0:
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)
            
            selection_object_label = self.form.tableWidget.item(row, column).text()

            selection_object = doc.getObjectsByLabel(selection_object_label)[0]
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(selection_object)
