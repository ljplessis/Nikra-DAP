




#TODO Include license


import FreeCAD
import DapTools
from FreeCAD import Units
from math import *
import os
import sys
import numpy as np
from PySide import QtCore
from PySide.QtCore import QProcess
#from PySide.QtCore import QProcess

JOINT_TRANSLATION = {"Rotation": "rev",
                     "Linear Movement": "tran"}

module_path = DapTools.get_module_path()
sys.path.append(os.path.join(module_path, "dap_solver"))


class DapSolverBuilder():
    
    
    
    def __init__(self, obj):
        self.obj = obj
        self.active_analysis = DapTools.getActiveAnalysis()
        self.doc_name = self.active_analysis.Document.Name
        self.doc = FreeCAD.getDocument(self.doc_name)
        
        self.dap_points = []
        self.dap_joints = []
        self.dap_forces = []
        
        
        
        
        self.t_initial = 0
        self.t_final = 1
        self.reporting_time = 0.01
        self.animate = True
        self.folder = "/tmp/"
        
        self.list_of_bodies = DapTools.getListOfBodyLabels()
        self.body_objects = DapTools.getListOfBodyObjects()
        self.material_object = DapTools.getMaterialObject()
        self.list_of_force_ojects = DapTools.getForcesObjects()
        
        if not(self.material_object):
            raise RuntimeError("No material defined")
        
        
        
        self.material_dictionary = self.material_object.MaterialDictionary
        
        FreeCAD.Console.PrintMessage("Initialising dap solver builder \n")
        FreeCAD.Console.PrintMessage("BUilder folder " + str(self.folder) + "\n")
        
        self.joints = DapTools.getListOfJointObjects()
        
        
        
        
        
        
        #TODO define the plane of movement using freecad gui
        #either by defining a principle axis or selecting planar Face/sketch/plane
        self.plane_norm = FreeCAD.Vector(0, 0, 1)
        #self.plane_norm = FreeCAD.Vector(0.49999999999999994, -0.5, 0.7071067811865477)
        
        self.plane_origin = FreeCAD.Vector(0, 0, 0) #NOTE assuming for now that plane moves through global origina
        
        
        
        #FreeCAD.Console.PrintMessage("Succesfully reloaded module \n")
        #FreeCAD.Console.PrintMessage("The Material Object \n")
        #FreeCAD.Console.PrintMessage(self.material_object.Label)
        #FreeCAD.Console.PrintMessage("\n")
        #FreeCAD.Console.PrintMessage("The Material Dictionary \n")
        #FreeCAD.Console.PrintMessage(self.material_dictionary)
        #FreeCAD.Console.PrintMessage("\n")
        #FreeCAD.Console.PrintMessage("List of bodies \n")
        #FreeCAD.Console.PrintMessage(self.list_of_bodies)
        #FreeCAD.Console.PrintMessage("\n")
        
        
        #TODO run a number of checkers
        #Checkers to run:
        #1.) There are bodies defined
        #2.) There are joints defined
        #3.) Check to make sure that not only ground parts are specified
        #4.) Make sure the same body part is not specified as both a ground and moving
        #5.) Check to make sure that there are moving bodies, and that everything is not by default ground
        #6.) Throw an error if both bodies of a joint is ground
        
        
        self.parts_of_bodies = {}
        for body_label in self.list_of_bodies:
            body_obj = self.doc.getObjectsByLabel(body_label)[0]
            list_of_parts = body_obj.References
            shape_complete_list = []
            for part in list_of_parts:
                part_obj = self.doc.getObjectsByLabel(part)[0]
                #body_object = FreeCAD.
                shape_label_list = DapTools.getListOfSolidsFromShape(part_obj, [])
                
                for part_sub_label in shape_label_list:
                    shape_complete_list.append(part_sub_label)
            self.parts_of_bodies[body_label] = shape_complete_list



        #FreeCAD.Console.PrintMessage("List of shapes parts of bodies \n")
        #FreeCAD.Console.PrintMessage(self.parts_of_bodies)
        #FreeCAD.Console.PrintMessage("\n")
        
    
        
        self.listOfMovingBodies()
        self.global_rotation_matrix = self.computeRotationMatrix()
        self.computeCentreOfGravity()
        self.computeMomentOfInertia()
        self.processJoints() #this includes processing points included within joints
        self.processForces()
        
        self.obj.global_rotation_matrix = self.global_rotation_matrix
        
        #self.writeBodies()
        #self.writePoints()
        #self.writeJoints()
        #self.writeForces()
        #self.writeFunctions()
        #self.writeUVectors()
        
        
        
        
        #from dapSolver import DapSolver
        #self.dapSolver = DapSolver(self.folder)
        
        
        
        #self.solve()
        
        #cog = self.cog_of_body_projected["DapBody"]
        #FreeCAD.Console.PrintMessage("Original cog:" + str(cog) + "\n")
        #FreeCAD.Console.PrintMessage("Rotated plane normal:" +  str(self.global_rotation_matrix*self.plane_norm) + "\n")
        #FreeCAD.Console.PrintMessage("Rotated centre of gravity:" +  str(self.global_rotation_matrix*cog) + "\n")
        #FreeCAD.Console.PrintMessage("Actual CoG: " + str(self.centre_of_gravity_of_body) +"\n")
        #FreeCAD.Console.PrintMessage("Projected CoG: " + str(self.cog_of_body_projected) +"\n")
        #FreeCAD.Console.PrintMessage("Rotated-projected CoG: " + str(self.cog_of_body_rotated) +"\n")
        
        #FreeCAD.Console.PrintMessage("List of joints: " + str(self.joints) + "\n")
        #self.projectPointOntoPlane(FreeCAD.Vector(10,10,10))
    
    def writeInputFiles(self):
        self.writeBodies()
        self.writePoints()
        self.writeJoints()
        self.writeForces()
        self.writeFunctions()
        self.writeUVectors()
    
    def processForces(self):
        for force_obj in self.list_of_force_ojects:
            FreeCAD.Console.PrintMessage("Force Object: " + str(force_obj.Label) + "\n")
            force = {}
            if force_obj.ForceTypes == "Gravity":
                
                gx = force_obj.gx.Value
                #FreeCAD.Console.PrintMessage("gx " + str(gx) + "\n")
                gy = force_obj.gy.Value
                gz = force_obj.gz.Value
                gravity_vector = FreeCAD.Vector(gx, gy, gz)
                gravity_mag = gravity_vector.Length
                gravity_norm = gravity_vector/gravity_mag
                
                gravity_norm_projected = self.projectPointOntoPlane(gravity_norm)
                gravity_norm_rotated = self.global_rotation_matrix*gravity_norm_projected
                
                force['type'] = 'weight'
                force['gravity'] = gravity_mag
                force['x'] = gravity_norm_rotated.x
                force['y'] = gravity_norm_rotated.y
                
                #FreeCAD.Console.PrintMessage("gravity mag " + str(gravity_mag) + "\n")
                #FreeCAD.Console.PrintMessage("gravity norm " + str(gravity_norm) + "\n")
                #FreeCAD.Console.PrintMessage("gravity norm projected" + str(gravity_norm_projected) + "\n")
                #FreeCAD.Console.PrintMessage("gravity norm rotated" + str(gravity_norm_rotated) + "\n")
            
            #TODO add additional force type
            
            self.dap_forces.append(force)
    
    def processJoints(self):
        for i in range(len(self.joints)):
            joint_type = JOINT_TRANSLATION[self.joints[i].JointType]
            
            if joint_type == "rev":
                joint1 = self.joints[i].Joint1
                joint1_coord = self.joints[i].Joint1Coord
                body1 = self.joints[i].Body1
                body2 = self.joints[i].Body2


                body1_index = self.extractDAPBodyIndex(body1)
                body2_index = self.extractDAPBodyIndex(body2)

                if body1_index == 0 and body2_index == 0:
                    raise RuntimeError("Both bodies attached to " + 
                                       str(self.joints[i].Label) + " were defined as ground.\n" +
                                       "The two bodies attached to the current joint are : " 
                                       + str(body1) + " and " +str(body2))
                
                iIndex = self.addDapPointUsingJointCoordAndBodyLabel(body1_index, body1, joint1_coord)
                
                jIndex = self.addDapPointUsingJointCoordAndBodyLabel(body2_index, body2, joint1_coord)
                
                self.addJoint(joint_type, iIndex, jIndex)
                #if the body is not ground, then the point coordinates should the local coordinate
                #with respect to the body CoG
                
                #FreeCAD.Console.PrintMessage("dapPoints " + str(self.dap_points) + "\n")
                #FreeCAD.Console.PrintMessage("dapJoints " + str(self.dap_joints) + "\n")
                #FreeCAD.Console.PrintMessage("body index 1 " + str(body1_index) +" \n")
                #FreeCAD.Console.PrintMessage("body index 2 " + str(body2_index) +" \n")

    def addJoint(self, joint_type, iIndex, jIndex):
            joint = {}
            joint["type"] = joint_type
            #NOTE: DAP.py is currently not 0 indexing, hence these indices should be 1 indexing
            joint["i"] = iIndex 
            joint["j"] = jIndex
            
            #TODO: if translation add uvectors
            
            self.dap_joints.append(joint)

    def addDapPointUsingJointCoordAndBodyLabel(self, body_index, body_label, point_coord):
        point = {}
        point['bIndex'] = body_index
        projected_coord = self.projectPointOntoPlane(point_coord)
        rotated_coord = self.global_rotation_matrix*projected_coord
        
        #FreeCAD.Console.PrintMessage("Body: " + str(body_label) + "\n")
        
        #FreeCAD.Console.PrintMessage("Projected coord " + str(projected_coord) + "\n")
        #FreeCAD.Console.PrintMessage("Projected-rotated coord " + str(rotated_coord) + "\n")
        # if body index =0, then connecting body is ground, and coordinates should be 
        # defined in the global coordinates based on the current logic
        if body_index == 0:
            point['x'] = rotated_coord.x
            point['y'] = rotated_coord.y
        else:
            #FreeCAD.Console.PrintMessage("Body rotated CoG: " + str(self.cog_of_body_rotated[body_label]) + "\n")
            bodyCoG = self.cog_of_body_rotated[body_label]
            point['x'] = rotated_coord.x - bodyCoG.x
            point['y'] = rotated_coord.y - bodyCoG.y
            
            #point['x'] =  bodyCoG.x - rotated_coord.x
            #point['y'] =  bodyCoG.y - rotated_coord.y
            
        self.dap_points.append(point)
        
        return len(self.dap_points)

    def extractDAPBodyIndex(self, body):
        if body == "Ground":
            body_index = 0
        else:
            test_index = self.list_of_bodies.index(body)
            body_type = self.body_objects[test_index].BodyType
            if body_type == "Ground":
                body_index = 0
            else:
                body_index = self.moving_bodies.index(body) + 1  #NOTE DAP.py is not 0 indexing
        return body_index
    #def collectAllPoints(self):
        #""" Loops over all possible objects which may have points and generates list of points """




        #return
    
    def listOfMovingBodies(self):
        self.moving_bodies = []
        
        #for body in self.body_objects:
        for i in range(len(self.body_objects)):
            if self.body_objects[i].BodyType == "Moving":
                self.moving_bodies.append(self.list_of_bodies[i])
    
    
    def computeRotationMatrix(self):
        """ Computes the rotation matrix, to rotate a given plane onto the xy plane. This is needed to
        transform all entities to be in an orthonormal axiss for the DAP analysis 
        Rotation matrix defined in 
        https://en.wikipedia.org/w/index.php?title=Rotation_matrix#Rotation_matrix_from_axis_and_angle
        """
        
        z = FreeCAD.Vector(0, 0, 1)
        #rotation_angle
        phi = acos(self.plane_norm * z)
        #axis_of_rotation
        u = self.plane_norm.cross(z)
        #FreeCAD.Console.PrintMessage("U: " + str(u) + "\n")
        #Adding in checker in case plane already in xy plane
        if u.Length > 0:
            u /= u.Length
        
        rotation_matrix = FreeCAD.Matrix()
        rotation_matrix.A11 = cos(phi) + u.x**2 * (1 - cos(phi))
        rotation_matrix.A21 = u.y*u.x*(1 - cos(phi)) + u.z*sin(phi)
        rotation_matrix.A31 = u.z*u.x*(1 - cos(phi)) - u.y*sin(phi)
        
        
        rotation_matrix.A12 = u.x*u.y*(1 - cos(phi)) - u.z*sin(phi)
        rotation_matrix.A22 = cos(phi) + u.y**2*(1-cos(phi))
        rotation_matrix.A32 = u.z*u.y*(1 - cos(phi)) + u.x*sin(phi)
        
        rotation_matrix.A13 = u.x*u.z*(1 - cos(phi)) + u.y*sin(phi)
        rotation_matrix.A23 = u.y*u.z*(1 - cos(phi)) - u.x*sin(phi)
        rotation_matrix.A33 = cos(phi) + u.z**2*(1 - cos(phi))
        
        #FreeCAD.Console.PrintMessage("Angle of rotation: " + str(phi) + "\n")
        #FreeCAD.Console.PrintMessage("Length of u: " + str(u.Length) + "\n")
        #FreeCAD.Console.PrintMessage("Length of planenorm: " + str(self.plane_norm.Length) + "\n")
        #FreeCAD.Console.PrintMessage("Axis of rotation: " + str(u) + "\n")
        #FreeCAD.Console.PrintMessage("Rotation Matrix: " + str(rotation_matrix) + "\n")
        #FreeCAD.Console.PrintMessage(u.x*u.y*(1 - cos(phi)) - u.z*sin(phi))
        #FreeCAD.Console.PrintMessage(self.plane_norm.Length)
        
        return rotation_matrix
    
    def projectPointOntoPlane(self, point):
        """ Projects a given vector onto the plane defined by the norm of the plane, passing through the (0,0,0) """
        projected_point = point - (self.plane_norm * (point - self.plane_origin)) * self.plane_norm
        
        #FreeCAD.Console.PrintMessage("Projected point " + str(point) + ": " + str(projected_point) + "\n")
        return projected_point
    
    def computeMomentOfInertia(self):
        """ Compute the moment of inertia of each body about the axis defined by the norm of the planar plane
        How: Computes J by matrixOfInertia dot plane_normal dot plane_normal.
        The global moment of inertia is then computed using the parallel axis theoram to sum the contribution
        of each local subshape within the global body container.
        """
        #FreeCAD.Console.PrintMessage("==============\n")
        #FreeCAD.Console.PrintMessage("Moment of intertia calculation: \n")
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
                
                #FreeCAD.Console.PrintMessage(str(Iij) + "\n")
                #FreeCAD.Console.PrintMessage("Moment of intertia about axis of rotation through COG: " + str(J) + "\n")
                
                #Project CoG of shape onto plane and compute distance of projected CoG of current shape to projected
                # body CoG
                centre_of_gravity = shape_obj.Shape.CenterOfMass
                CoG_me_proj = self.projectPointOntoPlane(centre_of_gravity)
                CoG_body_proj = self.cog_of_body_projected[body_label]
                planar_dist_CoG_to_CogBody = ((CoG_me_proj.x - CoG_body_proj.x)**2 + (CoG_me_proj.y - CoG_body_proj.y)**2 
                                       + (CoG_me_proj.z - CoG_body_proj.z)**2)**0.5
                
                
                shape_mass = shape_obj.Shape.Volume * density
                #NOTE: Using parallel axis theoram to compute the moment of inertia of the full body comprised of
                #multiple shapes
                J_global_body += J + shape_mass * planar_dist_CoG_to_CogBody**2
                
                #FreeCAD.Console.PrintMessage("Planar distance of CoG to CoG: " + str(planar_dist_CoG_to_CogBody) + "\n")
            
            #FreeCAD.Console.PrintMessage("Total J: " + str(J_global_body) + "\n")
            
            self.J[body_label] = J_global_body
            
            FreeCAD.Console.PrintMessage("Total J: " + str(self.J) + "\n")
            #Iij = 
    
    def computeCentreOfGravity(self):
        """  Computes the global centre of mass of each body based on the weighted sum of each subshape centre
        of grabity. """
        self.centre_of_gravity_of_body = {}
        self.cog_of_body_projected = {}
        self.cog_of_body_rotated = {}
        self.total_mass_of_body = {}
        #FreeCAD.Console.PrintMessage("======\nStarting centre of gravity computation\n")
        for body_label in self.list_of_bodies:
            #FreeCAD.Console.PrintMessage(body_label + "\n")
            #FreeCAD.Console.PrintMessage(str(self.parts_of_bodies[body_label]) + "\n")
            
            #total_mass = FreeCAD.Units.Quantity("0 kg")
            total_mass = 0
            centre_of_gravity_global = FreeCAD.Vector(0,0,0)
            for shape_label in self.parts_of_bodies[body_label]:
                
                #FreeCAD.Console.PrintMessage(shape_label)
                #FreeCAD.Console.PrintMessage("\n")
                
                
                shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                centre_of_gravity = shape_obj.Shape.CenterOfMass
                volume = shape_obj.Shape.Volume

                #NOTE: Converting density to base units which is mm?
                density = Units.Quantity(self.material_dictionary[shape_label]["density"]).Value
                mass = density*volume
                total_mass += mass
                
                centre_of_gravity_global += mass*centre_of_gravity
                
                #FreeCAD.Console.PrintMessage("Centre of gravity: " + str(centre_of_gravity) + "\n")
                #FreeCAD.Console.PrintMessage("density: " + str(density) + "\n")
                #FreeCAD.Console.PrintMessage("mass: " + str(mass) + "\n")
                
            centre_of_gravity_global /= total_mass
            self.centre_of_gravity_of_body[body_label] =  centre_of_gravity_global
            self.cog_of_body_projected[body_label] = self.projectPointOntoPlane(centre_of_gravity_global)
            self.total_mass_of_body[body_label] = total_mass
            self.cog_of_body_rotated[body_label] = self.global_rotation_matrix * self.cog_of_body_projected[body_label]
            
            #FreeCAD.Console.PrintMessage("Total mass: " +str(total_mass) + "\n")
            #FreeCAD.Console.PrintMessage("Global centre of mass: " +str(centre_of_gravity_global) + "\n")

        #FreeCAD.Console.PrintMessage("CoG: " + str(self.centre_of_gravity_of_body) + "\n")
        #FreeCAD.Console.PrintMessage("CoG projected: " + str(self.cog_of_body_projected) + "\n")
        #FreeCAD.Console.PrintMessage("Mass: " + str(self.total_mass_of_body) +"\n")
        
        
    #TODO: find a more elegant way of writing the input files instead of line by line writing
    def writeBodies(self):
        FreeCAD.Console.PrintMessage("Writing bodies \n")
        
        bodies = [None]
        file_path = os.path.join(self.folder,"inBodies.py")
        fid = open(file_path, 'w')
        fid.write("global Bodies \n")
        
        #for i in range(len(self.list_of_bodies)):
        for i in range(len(self.moving_bodies)):
            body_index = self.list_of_bodies.index(self.moving_bodies[i])
            fid.write("B"+str(i+1)+" = Body_struct()\n")
            fid.write("B"+str(i+1)+".m = " + str(self.total_mass_of_body[self.list_of_bodies[body_index]]) + "\n")
            fid.write("B"+str(i+1)+".J = " + str(self.J[self.list_of_bodies[body_index]]) + "\n")
            fid.write("B"+str(i+1)+".r = np.array([[" + str(self.cog_of_body_rotated[self.list_of_bodies[body_index]].x) + ","
                      + str(self.cog_of_body_rotated[self.list_of_bodies[body_index]].y) + "]]).T\n")
            fid.write("B"+str(i+1)+".p = " + str(0) + "\n")
            fid.write("\n")
            #bodies.append("B"+str(i))
        fid.write('Bodies = np.array([[None')
        for i in range(len(self.moving_bodies)):
            fid.write(', B'+str(i+1))
        fid.write("]]).T\n")
        fid.close()
        
    def writePoints(self):
        #FreeCAD.Console.PrintMessage(str(self.dap_points) + "\n")
        file_path = os.path.join(self.folder,"inPoints.py")
        fid = open(file_path, 'w')
        fid.write('global Points\n')
        for i in range(len(self.dap_points)):
            fid.write("P"+str(i+1)+" = Point_struct()\n")
            fid.write("P"+str(i+1)+".Bindex = " + str(self.dap_points[i]["bIndex"]) +"\n")
            sp_i = self.dap_points[i]["x"]
            sp_j = self.dap_points[i]["y"]
            fid.write("P"+str(i+1)+".sPlocal = np.array([[" + str(sp_i) + "," + str(sp_j) + "]]).T\n")
            fid.write("\n")
        
        fid.write('Points = np.array([[None')
        for i in range(len(self.dap_points)):
            fid.write(', P'+str(i+1))
        fid.write("]]).T\n")
        fid.close()

    def writeJoints(self):
        #FreeCAD.Console.PrintMessage(str(self.dap_joints)+"\n")
        file_path = os.path.join(self.folder,"inJoints.py")
        fid = open(file_path, 'w')
        fid.write('global Joints\n')
        for i in range(len(self.dap_joints)):
            fid.write("J"+str(i+1)+" = Joint_struct()\n")
            fid.write("J"+str(i+1)+".type = '" + str(self.dap_joints[i]["type"]) + "'\n")
            fid.write("J"+str(i+1)+".iPindex = " + str(self.dap_joints[i]["i"]) + "\n")
            fid.write("J"+str(i+1)+".jPindex = " + str(self.dap_joints[i]["j"]) + "\n")
            
            #TODO add uVectors if translational joint
            
            
            fid.write("\n")
            
        fid.write('Joints = np.array([[None')
        for i in range(len(self.dap_joints)):
            fid.write(', J'+str(i+1))
        fid.write("]]).T\n")
        fid.close()
        
        
    def writeForces(self):
        file_path = os.path.join(self.folder,"inForces.py")
        fid = open(file_path, 'w')
        fid.write('global Forces\n')
        for i in range(len(self.dap_forces)):
            fid.write("F"+str(i+1)+" = Force_struct()\n")
            fid.write("F"+str(i+1)+".type = '" + str(self.dap_forces[i]["type"]) + "'\n")
            if self.dap_forces[i]["type"] == 'weight':
                fid.write("F"+str(i+1)+".gravity = " + str(self.dap_forces[i]["gravity"]) + "\n")
                fid.write("F"+str(i+1)+".wgt = np.array([["+str(self.dap_forces[i]['x']) 
                          + ", " +str(self.dap_forces[i]['y']) + "]]).T\n")
            
            #TODO add uVectors if translational joint
            
            
            fid.write("\n")
            
        fid.write('Forces = np.array([[None')
        for i in range(len(self.dap_forces)):
            fid.write(', F'+str(i+1))
        fid.write("]]).T\n")
        fid.close()
        
    def writeFunctions(self):
        file_path = os.path.join(self.folder,"inFuncts.py")
        fid = open(file_path, 'w')
        fid.write('global Functs\n')
        
        #TODO include writer for functions
        fid.write("\n")
        fid.write("Functs = np.array([[]]).T\n")
    
    def writeUVectors(self):
        file_path = os.path.join(self.folder,"inUvectors.py")
        fid = open(file_path, 'w')
        fid.write('global Uvectors\n')
        
        #TODO include writer for UVectors, needed for translational joints
        fid.write("\n")
        fid.write("Uvectors = np.array([[]]).T\n")
        

    def solve(self):
        #NOTE: Temporary for temp dap python solver, create input settings file that can be read by main solver
        inputFile = os.path.join(self.folder,"dapInputSettings.py")
        fid = open(inputFile,'w')
        fid.write("animate = " + str(self.animate) + "\n")
        fid.write("t_initial = " + str(self.t_initial) + "\n")
        fid.write("dt = " + str(self.reporting_time) + "\n")
        fid.write("t_final = " + str(self.t_final) + "\n")
        fid.write("folder = '" + str(self.folder) + "'\n")
        fid.close()

        
        cwd = DapTools.get_module_path()
        dap_solver = os.path.join(cwd,"dap_solver","dap_temp.py")
        #exec(open(dap_solver).read())
        
        self.dapResults = None
        self.resultsAvailable = False
        self.obj.DapResults = None
        
        
        #self.process.finished.connect(self.loadResults)
        
        #cmd = "python3 " + str(dap_solver)
        #args = [str(self.folder)]
        
        #cmd = "python3"
        #args = [str(dap_solver),  str(self.folder)]
        
        #QString pythonCommand = "python3 " + str(dap_solver) + " " + str(self.folder)
        pythonCommand = "python3 " + str(dap_solver) + " " + str(self.folder)
        #FreeCAD.Console.PrintMessage(["python3", str(dap_solver),str(self.folder)])
        #FreeCAD.Console.PrintMessage(cmd + "\n")
        #self.process.start("python3",str(dap_solver),str(self.folder))
        
        #self.process.start(cmd, args)
        #self.process.start(pythonCommand)
        #self.process.start("python3",[str(dap_solver), str(self.folder)])
        
        from PySide.QtCore import QProcess
        #process = QProcess()
        self.process = QtCore.QProcess()
        self.process.finished.connect(self.onFinished)
        #process.
        #process.startDetached("dolphin")
        #process.start("dolphin"
        
        #F)
        #FreeCAD.Console.PrintMessage("Finished " + str(process.finished()))
        
        #process.setReadChannelMode(ForwardedChannels);
        #env = QtCore.QProcessEnvironment.systemEnvironment()
        #process.setProcessEnvironment(env)
        
        FreeCAD.Console.PrintMessage("DAP solver started.\n")
        
        self.process.start("python3",[str(dap_solver), str(self.folder)])
        ##proc.waitForStarted()
        #TODO need to overwrite waitForFinished to latch on to the output
        self.process.waitForFinished()
        
        #FreeCAD.Console.PrintMessage(process.waitForStarted())
        #FreeCAD.Console.PrintMessage("Process started \n")
        
        #import subprocess
        #self.solverCommand = subprocess.Popen(["python3", str(dap_solver),str(self.folder)])
        #self.dapSolverIsRunning = solverCommand.poll() is None 
        
        #subprocess.call(["python3", str(dap_solver),str(self.folder)])
        
        #print("T_Array from solve function",Tarray)
    def onFinished(self,  exitCode,  exitStatus):
        #FreeCAD.Console.PrintMessage("Solver finished on finished \n")
        #FreeCAD.Console.PrintMessage("Exit code " + str(exitCode) + " \n")
        #FreeCAD.Console.PrintMessage("exitStatus " + str(exitStatus) + " \n")
        
        if exitCode == 0:
            FreeCAD.Console.PrintMessage("Solver completed Succesfully \n")
            self.loadResults()
            self.resultsAvailable = True
        else:
            FreeCAD.Console.PrintError("Solver Failed: error codes not yet included (in the TODO list)\n")
        
    def loadResults(self):
        results = os.path.join(self.folder, "dapResults.npy")
        self.dapResults = np.load(results)
        self.obj.DapResults = self.dapResults.tolist()
        
        import pickle
        with open(os.path.join(self.folder,"Bodies_r"), "rb") as fp:   #Pickling
            self.obj.Bodies_r = pickle.load(fp)
        with open(os.path.join(self.folder,"Bodies_p"), "rb") as fp:   #Pickling
            self.obj.Bodies_p = pickle.load(fp)
        with open(os.path.join(self.folder,"Bodies_r_d"), "rb") as fp:   #Pickling
            self.obj.Bodies_r_d = pickle.load(fp)
        with open(os.path.join(self.folder,"Bodies_p_d"), "rb") as fp:   #Pickling
            self.obj.Bodies_p_d = pickle.load(fp)
        
        #FreeCAD.Console.PrintMessage("Results: "+str(self.dapResults) + "\n")
        #FreeCAD.Console.PrintMessage("Results (list): "+str(self.obj.DapResults) + "\n")
        #FreeCAD.Console.PrintMessage("Results loaded.\n")
        
        
        #self.obj.Bodies_r = []
        #self.obj.Bodies_p = []
        #for i in range():
            
        
        
        
        #FreeCAD.Console.PrintMessage(dapSolver)
        
        #from structures import Body_struct, Force_struct, Joint_struct, Point_struct, Unit_struct, Funct_struct
        
        #exec(open(os.path.join(self.folder, 'inBodies.py')).read())
        #exec(open(os.path.join(self.folder, 'inForces.py')).read())
        #exec(open(os.path.join(self.folder, 'inFuncts.py')).read())
        #exec(open(os.path.join(self.folder, 'inJoints.py')).read())
        #exec(open(os.path.join(self.folder, 'inPoints.py')).read())
        #exec(open(os.path.join(self.folder, 'inUvectors.py')).read())
        
        ##self.Bodies = Bodies
        ##self.
        
        #FreeCAD.Console.PrintMessage("Bodies " + str(Bodies) + "\n")
        
        #from initialize import initialize
        #initialize()
