




#TODO Include license


import FreeCAD
import DapTools
from FreeCAD import Units

class DapSolverBuilder():
    
    
    
    def __init__(self):
        self.active_analysis = DapTools.getActiveAnalysis()
        self.doc_name = self.active_analysis.Document.Name
        self.doc = FreeCAD.getDocument(self.doc_name)
        self.list_of_bodies = DapTools.getListOfBodyLabels()
        self.material_object = DapTools.getMaterialObject()
        
        self.material_dictionary = self.material_object.MaterialDictionary
        
        #TODO define the plane of movement using freecad gui
        #either by defining a principle axis or selecting planar Face/sketch/plane
        self.plane_norm = FreeCAD.Vector(0, 0, 1)
        self.plane_origin = FreeCAD.Vector(0, 0, 0) #NOTE assuming for now that plane moves through global origina
        
        
        
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
        #4.) Make sure the same body part is not specified as both a ground and moving
        
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
        #self.computeMomentOfInertia()
        #self.projectPointOntoPlane(FreeCAD.Vector(10,10,10))
    
    def projectPointOntoPlane(self, point):
        projected_point = point - (self.plane_norm * (point - self.plane_origin)) * self.plane_norm
        
        #FreeCAD.Console.PrintMessage("Projected point " + str(point) + ": " + str(projected_point) + "\n")
        return projected_point
    
    def computeMomentOfInertia(self):
        FreeCAD.Console.PrintMessage("==============\n")
        FreeCAD.Console.PrintMessage("Moment of intertia calculation: \n")
        #self.J = {}
        #self.J_projected = {}
        self.J = {}
        for body_label in self.list_of_bodies:
            J_global_body = 0
            for shape_label in self.parts_of_bodies[body_label]:
                shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                Iij = shape_obj.Shape.MatrixOfInertia
                density = Units.Quantity(self.material_dictionary[shape_label]["density"]).Value
                #Moment of inertia about axis of orientation (normal of plane)
                J = Iij * self.plane_norm * self.plane_norm  * density
                FreeCAD.Console.PrintMessage(str(Iij) + "\n")
                FreeCAD.Console.PrintMessage("Moment of intertia about axis of rotation through COG: " + str(J) + "\n")
                
                #Project CoG of shape onto plane and computer distance of projected CoG of current shape to projected
                # body CoG
                centre_of_gravity = shape_obj.Shape.CenterOfGravity
                CoG_me_proj = self.projectPointOntoPlane(centre_of_gravity)
                CoG_body_proj = self.cog_of_body_projected[body_label]
                planar_dist_CoG_to_CogBody = ((CoG_me_proj.x - CoG_body_proj.x)**2 + (CoG_me_proj.y - CoG_body_proj.y)**2 
                                       + (CoG_me_proj.z - CoG_body_proj.z)**2)**0.5
                
                
                shape_mass = shape_obj.Shape.Volume * density
                #NOTE: Using parallel axis theoram to compute the moment of inertia of the full body comprised of
                #multiple shapes
                J_global_body += J + shape_mass * planar_dist_CoG_to_CogBody**2
                FreeCAD.Console.PrintMessage("Planar distance of CoG to CoG: " + str(planar_dist_CoG_to_CogBody) + "\n")
            FreeCAD.Console.PrintMessage("Total J: " + str(J_global_body) + "\n")
            
            self.J[body_label] = J_global_body
            
            FreeCAD.Console.PrintMessage("Total J: " + str(self.J) + "\n")
            #Iij = 
    
    def computeCentreOfGravity(self):
        self.centre_of_gravity_of_body = {}
        self.cog_of_body_projected = {}
        self.total_mass_of_body = {}
        FreeCAD.Console.PrintMessage("======\nStarting centre of gravity computation\n")
        for body_label in self.list_of_bodies:
            FreeCAD.Console.PrintMessage(body_label + "\n")
            FreeCAD.Console.PrintMessage(str(self.parts_of_bodies[body_label]) + "\n")
            
            #total_mass = FreeCAD.Units.Quantity("0 kg")
            total_mass = 0
            centre_of_gravity_global = FreeCAD.Vector(0,0,0)
            for shape_label in self.parts_of_bodies[body_label]:
                
                FreeCAD.Console.PrintMessage(shape_label)
                FreeCAD.Console.PrintMessage("\n")
                shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                centre_of_gravity = shape_obj.Shape.CenterOfGravity
                volume = shape_obj.Shape.Volume

                #NOTE: Converting density to base units which is mm?
                density = Units.Quantity(self.material_dictionary[shape_label]["density"]).Value
                mass = density*volume
                total_mass += mass
                
                centre_of_gravity_global += mass*centre_of_gravity
                
                FreeCAD.Console.PrintMessage("Centre of gravity: " + str(centre_of_gravity) + "\n")
                FreeCAD.Console.PrintMessage("density: " + str(density) + "\n")
                
                FreeCAD.Console.PrintMessage("mass: " + str(mass) + "\n")
                
            centre_of_gravity_global /= total_mass
            self.centre_of_gravity_of_body[body_label] =  centre_of_gravity_global
            self.cog_of_body_projected[body_label] = self.projectPointOntoPlane(centre_of_gravity_global)
            self.total_mass_of_body[body_label] = total_mass
            FreeCAD.Console.PrintMessage("Total mass: " +str(total_mass) + "\n")
            FreeCAD.Console.PrintMessage("Global centre of mass: " +str(centre_of_gravity_global) + "\n")

        FreeCAD.Console.PrintMessage("CoG: " + str(self.centre_of_gravity_of_body) + "\n")
        FreeCAD.Console.PrintMessage("CoG projected: " + str(self.cog_of_body_projected) + "\n")
        FreeCAD.Console.PrintMessage("Mass: " + str(self.total_mass_of_body) +"\n")
