




#TODO Include license


import FreeCAD
import DapTools

class DapSolverBuilder():
    
    
    
    def __init__(self):
        self.active_analysis = DapTools.getActiveAnalysis()
        self.doc_name = self.active_analysis.Document.Name
        self.doc = FreeCAD.getDocument(self.doc_name)
        self.list_of_bodies = DapTools.getListOfBodyLabels()
        self.material_object = DapTools.getMaterialObject()
        
        self.material_dictionary = self.material_object.MaterialDictionary
        
        FreeCAD.Console.PrintMessage("Succesfully reloaded module \n")
        FreeCAD.Console.PrintMessage("The Material Object \n")
        FreeCAD.Console.PrintMessage(self.material_object.Label)
        FreeCAD.Console.PrintMessage("\n")
        FreeCAD.Console.PrintMessage("The Material Dictionary \n")
        FreeCAD.Console.PrintMessage(self.material_dictionary)
        FreeCAD.Console.PrintMessage("\n")
        FreeCAD.Console.PrintMessage("List of bodies \n")
        FreeCAD.Console.PrintMessage(self.list_of_bodies)
        FreeCAD.Console.PrintMessage("\n")
        
        
        #TODO run a number of checkers
        #Checkers to run:
        #1.) There are bodies defined
        #2.) There are joints defined
        #3.) Check to make sure that not only ground parts are specified
        
        self.parts_of_bodies = {}
        for body_label in self.list_of_bodies:
            body_obj = self.doc.getObjectsByLabel(body_label)[0]
            list_of_parts = body_obj.References
            shape_complete_list = []
            for part in list_of_parts:
                part_obj = self.doc.getObjectsByLabel(part)[0]
                #body_object = FreeCAD.
                shape_label_list = DapTools.getListOfSolidsFromShape(part_obj, [])
                

                FreeCAD.Console.PrintMessage("List of shapes as part of body: " + str(body_label) +"\n")
                FreeCAD.Console.PrintMessage(shape_label_list)
                FreeCAD.Console.PrintMessage("\n")



                for part_sub_label in shape_label_list:
                    shape_complete_list.append(part_sub_label)
            self.parts_of_bodies[body_label] = shape_complete_list



        FreeCAD.Console.PrintMessage("List of shapes parts of bodies \n")
        FreeCAD.Console.PrintMessage(self.parts_of_bodies)
        FreeCAD.Console.PrintMessage("\n")
        
    
        self.computeCentreOfGravity()
    
    def computeCentreOfGravity(self):
        FreeCAD.Console.PrintMessage("======\nStarting centre of gravity computation\n")
        for body_label in self.list_of_bodies:
            FreeCAD.Console.PrintMessage(body_label + "\n")
            FreeCAD.Console.PrintMessage(str(self.parts_of_bodies[body_label]) + "\n")
            
            for shape_label in self.parts_of_bodies[body_label]:
                
            shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
            density = 
            
