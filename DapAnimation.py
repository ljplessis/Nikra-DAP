 
 
#TODO Add license


import FreeCAD
import DapTools
from DapTools import addObjectProperty
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    
    
#def makeDapAnimation(name="DapAnimation"):
    ##obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    ##_DapAnimation(obj)
    #if FreeCAD.GuiUp:
        #_ViewProviderDapBody(obj.ViewObject)
    #return obj


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
        
        #testObject = DapTools.getSolverObject()
        
        if docName in FreeCAD.listDocuments():
            FreeCAD.setActiveDocument(docName)
        else:
            FreeCAD.newDocument(docName)
        animation_doc = FreeCAD.ActiveDocument
        #ugly workaround to remove all objects from the document upon restart
        for obj in animation_doc.Objects:
            animation_doc.removeObject(obj.Label)
        
        #body_objects = DapTools.getListOfBodyObjects()
        list_of_bodies = []
        for body in body_objects:
            animation_doc.addObject("Part::Feature", body.Label)
            animation_doc.getObject(body.Label).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)
        
        FreeCADGui.SendMsgToActiveView("ViewFit")
        
        
        
        import _TaskPanelAnimate
        ##testObject = DapTools.getSolverObject()
        taskd = _TaskPanelAnimate.TaskPanelAnimate(solver_doc, 
                                                   animation_doc, 
                                                   results, 
                                                   list_of_bodies, 
                                                   rotation_matrix,
                                                   Bodies_r,
                                                   Bodies_p)
        FreeCADGui.Control.showDialog(taskd)
        #FreeCAD.Console.PrintMessage("Attempting to get document which doesnt exist \n")
        #FreeCAD.Console.PrintMessage(FreeCAD.getDocument(docName))
        #DapTools.getActiveAnalysis().addObject(DapBodySelection.makeDapBody())
        #FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Dap_Animation', _CommandDapAnimation())


#class _DapAnimation:
    #def __init__(self, obj):
        #self.initProperties(obj)
        #obj.Proxy = self
        #self.Type = "DapAnimation"

        

    #def initProperties(self, obj):
        
        #return

    #def onDocumentRestored(self, obj):
        #self.initProperties(obj)

    #def execute(self, obj):
        #""" Create compound part at recompute. """
        ##docName = str(obj.Document.Name)
        ##doc = FreeCAD.getDocument(docName)
        ##shape_objects = []
        ##if len(obj.References)>0:
            ##for i in range(len(obj.References)):
                ##selection_object = doc.getObjectsByLabel(obj.References[i])[0]
                ##shape_objects.append(selection_object.Shape)
            ##shape = Part.makeCompound(shape_objects)
            ##obj.Shape = shape
        ##else:
            ##obj.Shape = Part.Shape()

        ##if shape is None:
            ##obj.Shape = Part.Shape()
        ##else:
            ##obj.Shape = shape

    #def __getstate__(self):
        #return None

    
    #def onChanged(self, obj, prop):
       
        #return

    #def __setstate__(self, state):
        #return None
    
#class _ViewProviderDapBody:
    #def __init__(self, vobj):
        #vobj.Proxy = self

    #def getIcon(self):
        #icon_path = os.path.join(DapTools.get_module_path(), "Gui", "Resources", "icons", "Icon8.png")
        #return icon_path

    #def attach(self, vobj):
        #self.ViewObject = vobj
        #self.Object = vobj.Object
        #self.standard = coin.SoGroup()
        #vobj.addDisplayMode(self.standard, "Standard")
        ##self.ViewObject.Transparency = 95
        #return

    #def getDisplayModes(self, obj):
        #modes = []
        #return modes

    #def getDefaultDisplayMode(self):
        ## TODO choose default display style
        ##return "Flat Lines"
        #return "Shaded"

    #def setDisplayMode(self,mode):
        #return mode

    #def updateData(self, obj, prop):
        #return


    #def doubleClicked(self, vobj):
        ##doc = FreeCADGui.getDocument(vobj.Object.Document)
        ##if not doc.getInEdit():
            ##doc.setEdit(vobj.Object.Name)
        ##else:
            ##FreeCAD.Console.PrintError('Task dialog already active\n')
        #return True

    #def setEdit(self, vobj, mode):
        ##import _TaskPanelDapBody
        ##taskd = _TaskPanelDapBody.TaskPanelDapBody(self.Object)
        ##FreeCADGui.Control.showDialog(taskd)
        #return True

    #def unsetEdit(self, vobj, mode):
        #FreeCADGui.Control.closeDialog()
        #return

    #def __getstate__(self):
        #return None

    #def __setstate__(self, state):
        #return None
