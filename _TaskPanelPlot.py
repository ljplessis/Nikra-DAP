 




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
import DapPlot

from freecad.plot import Plot

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide.QtGui import QFormLayout
    



class TaskPanelPlot:
    """ Taskpanel for adding DAP Bodies """
    def __init__(self):
        self.solver_object = DapTools.getSolverObject()
        self.doc = self.solver_object.Document
        
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelPlot.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        
        
        self.form.whatToPlotBox.addItems(DapPlot.PLOT_ITEMS)
        self.form.whatToPlotBox.currentIndexChanged.connect(self.whatToPlotChanged)
        
        self.plottableList = self.extractPlotableObjects()
        self.form.plottableItems.addItems(self.plottableList)
        self.form.plottableItems.currentIndexChanged.connect(self.plottableIndexChanged)
        
        self.form.addButton.clicked.connect(self.addButtonPushed)
        self.form.removeButton.clicked.connect(self.removeButtonPushed)
        
        self.form.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.form.tableWidget.cellClicked.connect(self.tableCellClicked)
        
        self.form.plotButton.clicked.connect(self.plotSelection)
        
    def tableCellClicked(self, row, column):
        object_label = self.form.tableWidget.item(row,0).text()
        FreeCAD.Console.PrintMessage(object_label)
        selection_object = self.doc.getObjectsByLabel(object_label)[0]
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(selection_object)
        
        
    def addButtonPushed(self):
        plottable_index = self.form.plottableItems.currentIndex()
        part_label = self.plottableList[plottable_index]
        if not(part_label in self.extractListOfObjectLabels()):
            table_row = self.form.tableWidget.rowCount()
            self.form.tableWidget.insertRow(table_row)
            item = QtGui.QTableWidgetItem(part_label)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.form.tableWidget.setItem(table_row, 0, item)
            
            item_legend = QtGui.QTableWidgetItem(part_label)
            self.form.tableWidget.setItem(table_row, 1, item_legend)
        
        
    def extractListOfObjectLabels(self):
        n_rows = self.form.tableWidget.rowCount()
        parts_list = []
        for row in range(n_rows):
            parts_list.append(self.form.tableWidget.item(row,0).text())
        return parts_list
        
    def removeButtonPushed(self):
        table_row = self.form.tableWidget.currentRow()
        self.form.tableWidget.removeRow(table_row)
        
    #def getPlottableItems(self):
    def plottableIndexChanged(self, index):
        selection_object = self.doc.getObjectsByLabel(self.plottableList[index])[0]
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Selection.addSelection(selection_object)
        
    def extractPlotableObjects(self):
        plot_list = []
        for item in list(self.solver_object.object_to_moving_body.keys()):
            plot_list.append(item)
        for item in list(self.solver_object.object_to_point.keys()):
            plot_list.append(item)
        return plot_list

    def reject(self):
        #Closes document and sets the active document back to the solver document
        FreeCADGui.Control.closeDialog()

    def getStandardButtons(self):
        return 0x00200000

    def whatToPlotChanged(self, index):
        if DapPlot.PLOT_ITEMS[index] == "Energy":
            self.form.spatialPlottingFrame.setVisible(False)
        else:
            self.form.spatialPlottingFrame.show()
    
    def extractObjectsAndLegend(self):
        n_rows = self.form.tableWidget.rowCount()
        parts_list = []
        legend_list = []
        for row in range(n_rows):
            parts_list.append(self.form.tableWidget.item(row,0).text())
            legend_list.append(self.form.tableWidget.item(row,1).text())
        return parts_list, legend_list
    
    def plotSelection(self):
        what_to_plot_index = self.form.whatToPlotBox.currentIndex()
        if DapPlot.PLOT_ITEMS[what_to_plot_index] != "Energy":
            parts_list, legend_list = self.extractObjectsAndLegend()
        else:
            
            #NOTE: example code of how to make subplots
            #self.fig = Plot.figure("Energy")
            #ax = self.fig.axes
            #ax.change_geometry(3,1,1)
            
            #potential_energy = self.solver_object.potential_energy
            #ax.set_title("Potential Energy")
            #ax.set_xlabel("Time [s]")
            #ax.set_ylabel("Potential Energy")
            #ax.plot(potential_energy)
            #self.fig.update()
            
            potential_energy = self.solver_object.potential_energy
            self.fig = Plot.figure("Potential Energy")
            self.fig.plot(potential_energy)
            #self.fig.update()
            
            
            
            #ax.
            #self.fig = Plot.subplot(FreeCAD.ActiveDocument.Name + "Residuals")
            #self.fig = Plot.figure(FreeCAD.ActiveDocument.Name + "Residuals")
            #ax = self.fig.add_subplot(222)
            #ax.plot([1,2],[1,2])
            #self.fig = Plot.Plot("random")
