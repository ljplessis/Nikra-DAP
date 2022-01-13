 




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
        self.form.tableWidget.cellChanged.connect(self.valueInCellChanged)


    def accept(self):
        self.obj.MaterialDictionary = self.MaterialDictionary
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return


    def reject(self):
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return True

    def valueInCellChanged(self):
        row = self.form.tableWidget.currentRow()
        col = self.form.tableWidget.currentColumn()

        # Only interested atm in changes that happen when user enters a custom density value
        if col == 2:
            part_label = self.form.tableWidget.item(row, 0).text()
            combo_box_object = self.form.tableWidget.cellWidget(row,1)
            mat_index = combo_box_object.currentIndex()
            current_mat_choice = self.card_name_list[mat_index]

            changed_text = self.form.tableWidget.item(row, col).text()

            self.MaterialDictionary[part_label] = {"matName": current_mat_choice[0],
                                                   "density" : changed_text}

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
        table_row = 0

        docName = str(self.doc_name)
        doc = FreeCAD.getDocument(docName)
        self.form.tableWidget.clearContents()
        self.form.tableWidget.setRowCount(0)
        self.form.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        if len(self.body_labels):
            selection_object = doc.getObjectsByLabel(self.body_labels[ci])[0]
            list_of_parts = selection_object.References
            #for part in list_of_parts:
            #for i in range(len(list_of_parts)):
            for current_body_label in list_of_parts:
                self.form.tableWidget.insertRow(table_row)
                
                #current_body_label = list_of_parts[i]
                obj = doc.getObjectsByLabel(current_body_label)[0]
                shape_label_list = DapTools.getListOfSolidsFromShape(obj, [])
                
                
                FreeCAD.Console.PrintMessage("List of parts loop, current part: " + str(current_body_label)+ "\n")
                
                FreeCAD.Console.PrintMessage(str(obj.Label) + "\n")
                FreeCAD.Console.PrintMessage("Subshapes: \n")
                FreeCAD.Console.PrintMessage(shape_label_list)
                FreeCAD.Console.PrintMessage("\n")
                
                if len(shape_label_list)>1:
                    partName = QtGui.QTableWidgetItem(current_body_label)
                    partName.setFlags(QtCore.Qt.ItemIsEnabled)
                    font = QtGui.QFont()
                    font.setBold(True)
                    partName.setFont(font)
                    self.form.tableWidget.setItem(table_row,0,partName)
                    table_row += 1

                for sub_shape_label in shape_label_list:
                    self.form.tableWidget.insertRow(table_row)
                    partName = QtGui.QTableWidgetItem(sub_shape_label)
                    partName.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.form.tableWidget.setItem(table_row,0,partName)
                    
                    
                
                    combo = QtGui.QComboBox()
                    for mat in self.card_name_list:
                        combo.addItem(QtGui.QIcon(mat[2]), mat[0], mat[1])

                
                    self.form.tableWidget.setCellWidget(table_row,1,combo)
                    


                    #TODO: a lot of code duplication between the various functions.
                    if sub_shape_label in self.MaterialDictionary.keys():
                        mat_name = self.MaterialDictionary[sub_shape_label]["matName"]
                        density = self.MaterialDictionary[sub_shape_label]["density"]
                        mi = indexOrDefault(self.card_name_labels, mat_name, 0)
                        combo.setCurrentIndex(mi)
                        density_item = QtGui.QTableWidgetItem(density)
                        self.form.tableWidget.setItem(table_row, 2, density_item)
                        # NOTE: if index != 0, then it is a pre-defined freecad material, which cannot be edited
                        # Not sure if this behaviour should be forced.
                        if mi != 0:
                            density_item.setFlags(QtCore.Qt.ItemIsEnabled)

                    combo.currentIndexChanged.connect(self.materialComboChanged)
                    table_row += 1

    def materialComboChanged(self, index):
        current_row = self.form.tableWidget.currentRow()
        current_mat_choice = self.card_name_list[index]
        if index == 0:
            density = self.default_density
        else:
            density = self.materials[current_mat_choice[1]]["Density"]

        density_item = QtGui.QTableWidgetItem(str(density))
        
        if index != 0:
            #NOTE This disables editing of the density value if it is selected from
            #available freeCAD materials. Not sure we should really force this?
            density_item.setFlags(QtCore.Qt.ItemIsEnabled)

        self.form.tableWidget.setItem(current_row, 2, density_item)
        part_label = self.form.tableWidget.item(current_row, 0).text()
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
