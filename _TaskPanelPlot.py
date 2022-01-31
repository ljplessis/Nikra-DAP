 




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
        #FreeCAD.Console.PrintMessage(object_label)
        label = object_label
        if ":" in label:
            selectable = label.split(":")[0]
        else:
            selectable = label
        selection_object = self.doc.getObjectsByLabel(selectable)[0]
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
        
    def plottableIndexChanged(self, index):
        label = self.plottableList[index]
        if ":" in label:
            selectable = label.split(":")[0]
        else:
            selectable = label
        selection_object = self.doc.getObjectsByLabel(selectable)[0]
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

    def extractPlotDispVel(self, parts_list, times, type):
        x_list = []
        y_list = []
        #legend_list = []
        for i in range(len(parts_list)):
            part = parts_list[i]
            x = []
            y = []
            if part in list(self.solver_object.object_to_moving_body.keys()):
                body_index = self.solver_object.object_to_moving_body[part]
                for timeIndex in range(len(times)):
                    if type == "Position" or type == "Path Trace":
                        x.append(self.solver_object.Bodies_r[timeIndex][body_index][0])
                        y.append(self.solver_object.Bodies_r[timeIndex][body_index][1])
                    if type == "Velocity":
                        x.append(self.solver_object.Bodies_r_d[timeIndex][body_index][0])
                        y.append(self.solver_object.Bodies_r_d[timeIndex][body_index][1])
            if part in list(self.solver_object.object_to_point.keys()):
                point_index = self.solver_object.object_to_point[part]
                FreeCAD.Console.PrintMessage("In extract plot disp vel, part: " + str(part) + "\n")
                FreeCAD.Console.PrintMessage("In extract plot disp vel, point_index: " + str(point_index) + "\n")
                FreeCAD.Console.PrintMessage("In extract plot disp vel, self.solver_object.object_to_point.keys(): " + str(self.solver_object.object_to_point.keys()) + "\n")
                
                for timeIndex in range(len(times)):
                    if type == "Position" or type == "Path Trace":
                        x.append(self.solver_object.Points_r[timeIndex][point_index][0])
                        y.append(self.solver_object.Points_r[timeIndex][point_index][1])
                    if type == "Velocity":
                        x.append(self.solver_object.Points_r_d[timeIndex][point_index][0])
                        y.append(self.solver_object.Points_r_d[timeIndex][point_index][1])
            x_list.append(x)
            y_list.append(y)
            
        return x_list, y_list
    
    def convertOrthonormalToReal(self, x_list, y_list):
        """ This function takes the list of x and y coordinates/velocities
        and rotates them into the 3D space using the inverse of the orthonormal rotation matrix.
        """
        x = []
        y = []
        z = []
        for j in range(len(x_list)):
            x_temp = []
            y_temp = []
            z_temp = []
            for i in range(len(x_list[j])):
                rot_mat = self.solver_object.global_rotation_matrix
                vec = FreeCAD.Vector(x_list[j][i], y_list[j][i], 0)
                rotated_vec = rot_mat.transposed().multVec(vec)
                x_temp.append(rotated_vec.x)
                y_temp.append(rotated_vec.y)
                z_temp.append(rotated_vec.z)
            x.append(x_temp)
            y.append(y_temp)
            z.append(z_temp)
        return x, y, z

    def plotSelection(self):
        what_to_plot_index = self.form.whatToPlotBox.currentIndex()
        what_to_plot = DapPlot.PLOT_ITEMS[what_to_plot_index]
        if what_to_plot != "Energy":
            parts_list, legend_list = self.extractObjectsAndLegend()
            times = self.solver_object.ReportedTimes
            
            if self.form.orthonormalRadioButton.isChecked():
                if what_to_plot == "Position" or what_to_plot == "Velocity":
                    fig = Plot.figure(what_to_plot)
                    ax = fig.axes
                    
                    x_list, y_list = self.extractPlotDispVel(parts_list, times, what_to_plot)

                    ax.change_geometry(2,1,1)
                    ax.set_title(what_to_plot)
                    ax.set_ylabel("x [units?]")
                    for i in range(len(x_list)):
                        ax.plot(times, x_list[i], label=legend_list[i])
                    ax.legend(loc='lower left')
                    
                    
                    
                    ax = fig.fig.add_subplot(2,1,2)
                    ax.change_geometry(2,1,2)
                    ax.set_xlabel("Time [s]")
                    ax.set_ylabel("y [units?]")
                    for i in range(len(y_list)):
                        ax.plot(times, y_list[i], label=legend_list[i])
                    ax.legend(loc='lower left')
                    
                    fig.update()

                elif what_to_plot == "Path Trace":
                    fig = Plot.figure("Path Trace")
                    
                    x_list, y_list = self.extractPlotDispVel(parts_list, times, what_to_plot)
                    
                    ax = fig.axes
                    
                    for i in range(len(x_list)):
                        FreeCAD.Console.PrintMessage(x_list)
                        ax.scatter(x_list[i], y_list[i], label=legend_list[i])
                    ax.legend(loc='lower left')
                    fig.update()

            if self.form.realRadioButton.isChecked():
                if what_to_plot == "Position" or what_to_plot == "Velocity":
                    fig = Plot.figure(what_to_plot)
                    ax = fig.axes
                    
                    x_list, y_list = self.extractPlotDispVel(parts_list, times, what_to_plot)
                    x_list, y_list, z_list = self.convertOrthonormalToReal(x_list, y_list)

                    ax.change_geometry(3,1,1)
                    ax.set_title(what_to_plot)
                    ax.set_ylabel("x [units?]")
                    for i in range(len(x_list)):
                        ax.plot(times, x_list[i], label=legend_list[i])
                    ax.legend(loc='lower left')
                    
                    ax = fig.fig.add_subplot(3,1,2)
                    ax.set_xlabel("Time [s]")
                    ax.set_ylabel("y [units?]")
                    for i in range(len(y_list)):
                        ax.plot(times, y_list[i], label=legend_list[i])
                        
                    ax = fig.fig.add_subplot(3,1,3)
                    ax.set_xlabel("Time [s]")
                    ax.set_ylabel("z [units?]")
                    for i in range(len(y_list)):
                        ax.plot(times, z_list[i], label=legend_list[i])

                    ax.legend(loc='lower left')
                    fig.update()
                    
                if what_to_plot == "Path Trace":
                    fig = Plot.figure("Path Trace")
                    
                    x_list, y_list = self.extractPlotDispVel(parts_list, times, what_to_plot)
                    x_list, y_list, z_list = self.convertOrthonormalToReal(x_list, y_list)
                    from mpl_toolkits.mplot3d import Axes3D
                    #NOTE: to get around the deprecated warning, creating new axis
                    #instance, and hiding previous isntance. Pehaps until FreeCAD.plot 
                    #module has been updated to custom create a new axis on init
                    ax1 = fig.axes
                    ax1.set_visible(False)
                    
                    ax = fig.fig.add_subplot(2,1,1,projection='3d')
                    ax.change_geometry(1,1,1)
                    for i in range(len(x_list)):
                        ax.scatter(x_list[i], y_list[i], z_list[i], label = legend_list[i])
                    ax.set_xlabel('x [units ?]')
                    ax.set_ylabel('y [units ?]')
                    ax.set_zlabel('z [units ?]')
                    ax.legend(loc='lower left')
                    
                    fig.update()
        else:
            times = self.solver_object.ReportedTimes
            
            potential_energy = self.solver_object.potential_energy
            fig = Plot.figure("Potential Energy")
            fig.plot(times, potential_energy)
            ax = fig.axes
            ax.set_title("Potential Energy")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Potential Energy [units?]")
            
            kinetic_energy = self.solver_object.kinetic_energy
            fig = Plot.figure("Kinetic Energy")
            fig.plot(times, kinetic_energy)
            ax = fig.axes
            ax.set_title("Kinetic Energy")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Kinetic Energy [units?]")
            
            total_energy = self.solver_object.total_energy
            fig = Plot.figure("Total Energy")
            fig.plot(times, total_energy)
            ax = fig.axes
            ax.set_title("Total Energy")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Total Energy [units?]")

