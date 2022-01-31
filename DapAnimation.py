 
 
#TODO Add license


import FreeCAD
import DapTools
from DapTools import addObjectProperty
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    


class _CommandDapAnimation:
    def GetResources(self):
        icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon8.png")
        return {
            'Pixmap': icon_path,
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Animation", "Animate solution"),
            #'Accel': "C, B",
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Animation", "Animates the motion of the moving bodies")}

    def IsActive(self):
        return DapTools.getSolverObject().DapResults is not None

    def Activated(self):
        import DapTools
        import DapAnimation
        
        solver_doc = FreeCAD.ActiveDocument
        
        docName = "Animation"
        body_objects = DapTools.getListOfBodyObjects()
        solver_object = DapTools.getSolverObject()
        results = solver_object.DapResults
        rotation_matrix = solver_object.global_rotation_matrix
        Bodies_r = solver_object.Bodies_r
        Bodies_p = solver_object.Bodies_p
        
        if docName in FreeCAD.listDocuments():
            FreeCAD.setActiveDocument(docName)
        else:
            FreeCAD.newDocument(docName)
        animation_doc = FreeCAD.ActiveDocument


        

        list_of_bodies = []
        for body in body_objects:
            a = animation_doc.addObject("Part::Feature", body.Label)
            #FreeCAD.Console.PrintMessage("In animate body.label: ")
            animation_doc.getObject(a.Name).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)
        
        FreeCADGui.SendMsgToActiveView("ViewFit")
        
        
        
        import _TaskPanelAnimate
        taskd = _TaskPanelAnimate.TaskPanelAnimate(solver_object,
                                                   solver_doc,
                                                   animation_doc,
                                                   results,
                                                   list_of_bodies,
                                                   rotation_matrix,
                                                   Bodies_r,
                                                   Bodies_p)
        FreeCADGui.Control.showDialog(taskd)



if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Animation', _CommandDapAnimation())

