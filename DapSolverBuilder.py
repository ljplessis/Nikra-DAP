




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
        
        self.parts_shape_list_all, self.parent_assembly_all = DapTools.getSolidsFromAllShapes(self.doc)
        
        self.dap_points = []
        self.dap_joints = []
        self.dap_forces = []
        self.dap_uvectors = []
        self.dap_funcs = []
        
        self.scale = 1e-3 #convert mm to m
        
        
        self.t_initial = self.obj.StartTime
        self.t_final = self.obj.EndTime
        self.reporting_time = self.obj.ReportingTimeStep
        self.animate = False
        self.folder = self.obj.FileDirectory
        
        self.list_of_bodies = DapTools.getListOfBodyLabels()
        self.body_objects = DapTools.getListOfBodyObjects()
        self.material_object = DapTools.getMaterialObject()
        self.list_of_force_ojects = DapTools.getForcesObjects()
        
        if not(self.material_object):
            raise RuntimeError("No material defined")
        
        multiple_gravity_bool = DapTools.gravityChecker()
        if multiple_gravity_bool:
            raise RuntimeError("More than one gravity was specified")
        
        self.material_dictionary = self.material_object.MaterialDictionary
        
        #FreeCAD.Console.PrintMessage("Initialising dap solver builder \n")
        #FreeCAD.Console.PrintMessage("BUilder folder " + str(self.folder) + "\n")
        
        self.joints = DapTools.getListOfJointObjects()
        
        
        
        self.plane_norm = self.obj.UnitVector
        
        #NOTE: for calculations it does not matter what the origin of the projection planeis
        self.plane_origin = FreeCAD.Vector(0, 0, 0) #NOTE assuming for now that plane moves through global origina
        

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
                #shape_label_list = DapTools.getListOfSolidsFromShape(part_obj, [])
                shape_label_list = self.parts_shape_list_all[part_obj.Label]
                for part_sub_label in shape_label_list:
                    shape_complete_list.append(part_sub_label)
            self.parts_of_bodies[body_label] = shape_complete_list


        self.listOfMovingBodies()
        self.global_rotation_matrix = self.computeRotationMatrix()
        self.computeCentreOfGravity()
        self.computeMomentOfInertia()
        self.processBodyInitialConditions()
        self.processJoints() #this includes processing points included within joints
        self.processForces()
        
        self.obj.global_rotation_matrix = self.global_rotation_matrix
        

    
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
            if force_obj.ForceTypes == "Rotational Spring" or force_obj.ForceTypes == "Rotational Spring Damper":
                if force_obj.Joint1 == "":
                    raise RuntimeError("Point 1 for " + str(force_obj.Label) + " was not defined")
            if force_obj.ForceTypes == "Spring" or force_obj.ForceTypes == "Linear Spring Damper":
                if force_obj.Joint1 == "":
                    raise RuntimeError("Point 1 for " + str(force_obj.Label) + " was not defined")
                if force_obj.Joint2 == "":
                    raise RuntimeError("Point 2 for " + str(force_obj.Label) + " was not defined")
            
            force = {}
            if force_obj.ForceTypes == "Gravity":
                
                gx = force_obj.gx.getValueAs("m/s^2")
                #FreeCAD.Console.PrintMessage("gx " + str(gx) + "\n")
                gy = force_obj.gy.getValueAs("m/s^2")
                gz = force_obj.gz.getValueAs("m/s^2")
                gravity_vector = FreeCAD.Vector(gx, gy, gz)
                gravity_mag = gravity_vector.Length
                gravity_norm = gravity_vector/gravity_mag
                
                gravity_norm_projected = self.projectPointOntoPlane(gravity_norm)
                gravity_norm_rotated = self.global_rotation_matrix*gravity_norm_projected
                
                force['type'] = "'weight'"
                force['gravity'] = gravity_mag
                force['wgt'] = "np.array([[" + str(gravity_norm_rotated.x) + "," + str(gravity_norm_rotated.y)+"]]).T"
                #gravity_mag
                #force['x'] = gravity_norm_rotated.x
                #force['y'] = gravity_norm_rotated.y
                

            #TODO add additional force type
            if force_obj.ForceTypes == "Spring" or force_obj.ForceTypes == "Linear Spring Damper":
                L0 = force_obj.UndeformedLength.getValueAs("m")
                k = force_obj.Stiffness.getValueAs("N/m")
                force_coord_1 = force_obj.JointCoord1 * self.scale
                force_coord_2 = force_obj.JointCoord2 * self.scale
                Joint1 = force_obj.Joint1
                Joint2 = force_obj.Joint2
                body1 = force_obj.Body1
                body2 = force_obj.Body2

                body1_index = self.extractDAPBodyIndex(body1)
                body2_index = self.extractDAPBodyIndex(body2)
                
                iIndex = self.addDapPointUsingJointCoordAndBodyLabel(body1_index, body1, force_coord_1)
                
                if body1_index != 0:
                    self.obj.object_to_point[str(force_obj.Label)+":"+str(Joint1)] = iIndex - 1
                
                jIndex = self.addDapPointUsingJointCoordAndBodyLabel(body2_index, body2, force_coord_2)
                
                if body2_index != 0:
                    self.obj.object_to_point[str(force_obj.Label)+":"+str(Joint2)] = jIndex - 1
                
                #self.addJoint(joint_type, iIndex, jIndex)
                force['type'] = "'ptp'"
                force['iPindex'] = iIndex
                force['jPindex'] = jIndex
                force['k'] = k
                force['L0'] = L0
                if force_obj.ForceTypes == "Linear Spring Damper":
                    force['dc'] = force_obj.LinDampCoeff.getValueAs("kg/s")

            if force_obj.ForceTypes == "Rotational Spring" or force_obj.ForceTypes == "Rotational Spring Damper":
                Joint1 = force_obj.Joint1
                force_coord_1 = force_obj.JointCoord1 * self.scale
                body1 = force_obj.Body1
                body2 = force_obj.Body2
                undeformed_angle = force_obj.UndeformedAngle.getValueAs("rad")
                rot_stiffness = force_obj.RotStiffness.getValueAs("m^2*kg/(s^2*rad)")
                
                body1_index = self.extractDAPBodyIndex(body1)
                body2_index = self.extractDAPBodyIndex(body2)
                
                #iIndex = self.addDapPointUsingJointCoordAndBodyLabel(body1_index, body1, force_coord_1)
                
                #if body1_index != 0:
                    #self.obj.object_to_point[str(force_obj.Label)] = iIndex - 1
                
                #jIndex = self.addDapPointUsingJointCoordAndBodyLabel(body2_index, body2, force_coord_1)
                force['type'] = "'rot_sda'"
                force['iBindex'] = body1_index
                force['jBindex'] = body2_index
                force['k'] = rot_stiffness
                force['theta0'] = undeformed_angle
                if force_obj.ForceTypes == "Rotational Spring Damper":
                    force['dc'] = force_obj.RotDampCoeff.getValueAs("(J*s)/rad")
                
            self.dap_forces.append(force)
            
    def processBodyInitialConditions(self):
        self.body_init = {}
        for i in range(len(self.body_objects)):
            body_label = self.list_of_bodies[i]
            body_object = self.body_objects[i]
            
            #at the moment the initial conditions are already specified in orthonormal co-ordinates
            #if the decision is made to at some point rather specify it in x-y-z coordinates then
            #the intiial condition should be projected and rotated onto the plane of motion
            self.body_init[body_label] = {}
            self.body_init[body_label]["init_y"] = body_object.InitialVertical.getValueAs("m/s")
            self.body_init[body_label]["init_x"] = body_object.InitialHorizontal.getValueAs("m/s")
            self.body_init[body_label]["init_p"] = body_object.InitialAngular.getValueAs("rad/s")
            
            
        
    def processJoints(self):
        for i in range(len(self.joints)):
            joint_type = JOINT_TRANSLATION[self.joints[i].TypeOfRelMov]

            #Checking definitions for consistency and completeness
            if joint_type == "rev":
                if self.joints[i].Point1RelMov == "":
                    raise RuntimeError("Point for " + str(self.joints[i].Label) + " was not defined")
            if joint_type == "tran":
                if self.joints[i].Point1RelMov == "":
                    raise RuntimeError("Point 1 for " + str(self.joints[i].Label) + " was not defined")
                if self.joints[i].Point2RelMov == "":
                    raise RuntimeError("Point 2 for " + str(self.joints[i].Label) + " was not defined")
            
            joint1_coord = self.joints[i].CoordPoint1RelMov * self.scale
            joint2_coord = self.joints[i].CoordPoint2RelMov * self.scale
            body1 = self.joints[i].Body1
            body2 = self.joints[i].Body2


            body1_index = self.extractDAPBodyIndex(body1)
            body2_index = self.extractDAPBodyIndex(body2)
            
            if body1_index == 0 and body2_index == 0:
                raise RuntimeError("Both bodies attached to " + 
                                    str(self.joints[i].Label) + " were defined as ground.\n" +
                                    "The two bodies attached to the current joint are : " 
                                    + str(body1) + " and " +str(body2))
            
            
            if joint_type == "rev":
                iIndex = self.addDapPointUsingJointCoordAndBodyLabel(body1_index, body1, joint1_coord)
                
                self.obj.object_to_point[self.joints[i].Label] = iIndex - 1
                jIndex = self.addDapPointUsingJointCoordAndBodyLabel(body2_index, body2, joint1_coord)
                
                self.addJoint(joint_type, iIndex, jIndex)

                
            elif joint_type == "tran":
                iIndex = self.addDapPointUsingJointCoordAndBodyLabel(body1_index, body1, joint1_coord)
                jIndex = self.addDapPointUsingJointCoordAndBodyLabel(body2_index, body2, joint2_coord)
                
                
                iUIndex, jUIndex = self.addUnitVectorBetweenTwoPoints(self.joints[i].Label,
                                                                      body1_index,
                                                                      body2_index,
                                                                      joint1_coord,
                                                                      joint2_coord,
                                                                      body1,
                                                                      body2)
                
                #NOTE: dap solver is 1 indexing but rest of code is not
                if body1_index != 0:
                    self.obj.object_to_point[str(self.joints[i].Label)+":"+str(self.joints[i].Point1RelMov)] = iIndex-1
                if body2_index != 0:
                    self.obj.object_to_point[str(self.joints[i].Label)+":"+str(self.joints[i].Point2RelMov)] = jIndex-1
                
                self.addJoint(joint_type, iIndex, jIndex, iUIndex=iUIndex, jUIndex=jUIndex)


    def addUnitVectorBetweenTwoPoints(self, 
                                      joint_label,
                                      body_index_1, 
                                      body_index_2, 
                                      body1_coord, 
                                      body2_coord, 
                                      body1_label, 
                                      body2_label):
        
        uVector = body2_coord - body1_coord
        if uVector.Length == 0:
            raise RuntimeError('The two points defining the movement "' + str(joint_label) +
            '" are the same. Please ensure the points are at different locations (attached to two different bodies.')
        else:
            #uVector = uVector.normalize()
            projected_vector = self.projectPointOntoPlane(uVector)
            rotated_vector = self.global_rotation_matrix*projected_vector
            uVector = rotated_vector.normalize()
            
            uvector_out = {}
            uvector_out["Bindex"] = body_index_1
            uvector_out["uLocal"] = "np.array([[" + str(uVector.x) +"," + str(uVector.y) +"]]).T"
            self.dap_uvectors.append(uvector_out)
            iIndex = len(self.dap_uvectors)
            
            uvector_out = {}
            uvector_out["Bindex"] = body_index_2
            uvector_out["uLocal"] = "np.array([[" + str(uVector.x) +"," + str(uVector.y) +"]]).T"
            self.dap_uvectors.append(uvector_out)
            jIndex = len(self.dap_uvectors)
            
            #FreeCAD.Console.PrintMessage("UVECTOR: " + str(self.dap_uvectors) + "\n")
            
            
        #dap_uvectors
        return iIndex, jIndex

    def addJoint(self, joint_type, iIndex, jIndex, iUIndex=0, jUIndex=0, iBindex=0, jBindex=0, iFunc=0):
            joint = {}
            joint["type"] = "'"+str(joint_type)+"'"
            if joint_type == "tran" or joint_type == "rev":
                #NOTE: DAP.py is currently not 0 indexing, hence these indices should be 1 indexing
                joint["iPindex"] = iIndex 
                joint["jPindex"] = jIndex
                
                #NOTE: DAP.py is currently not 0 indexing, hence these indices should be 1 indexing
                if joint_type == "tran":
                    joint["iUindex"] = iUIndex
                    joint["jUindex"] = jUIndex
            elif joint_type == "rel-rot":
                joint["iBindex"] = iBindex
                joint["jBindex"] = jBindex
                joint["iFunct"] = iFunc
            
            self.dap_joints.append(joint)

    def addDapPointUsingJointCoordAndBodyLabel(self, body_index, body_label, point_coord):
        point = {}
        point['Bindex'] = body_index
        projected_coord = self.projectPointOntoPlane(point_coord)
        rotated_coord = self.global_rotation_matrix*projected_coord
        
        # if body index =0, then connecting body is ground, and coordinates should be 
        # defined in the global coordinates based on the current logic
        if body_index == 0:
            point["sPlocal"] = "np.array([[" + str(rotated_coord.x) + "," + str(rotated_coord.y) + "]]).T"
        else:
            #FreeCAD.Console.PrintMessage("Body rotated CoG: " + str(self.cog_of_body_rotated[body_label]) + "\n")
            bodyCoG = self.cog_of_body_rotated[body_label]
            x = rotated_coord.x - bodyCoG.x
            y = rotated_coord.y - bodyCoG.y
            point["sPlocal"] = "np.array([[" + str(x) + "," + str(y) + "]]).T"
            
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

        #return
    
    def listOfMovingBodies(self):
        self.moving_bodies = []
        
        #for body in self.body_objects:
        for i in range(len(self.body_objects)):
            if self.body_objects[i].BodyType == "Moving":
                self.moving_bodies.append(self.list_of_bodies[i])
                
                self.obj.object_to_moving_body[self.body_objects[i].Label] = i
    
    
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
        
        
        return rotation_matrix
    
    def projectPointOntoPlane(self, point):
        """ Projects a given vector onto the plane defined by the norm of the plane, passing through the (0,0,0) """
        projected_point = point - (self.plane_norm * (point - self.plane_origin)) * self.plane_norm
        
        return projected_point
    
    def computeMomentOfInertia(self):
        """ Compute the moment of inertia of each body about the axis defined by the norm of the planar plane
        How: Computes J by matrixOfInertia dot plane_normal dot plane_normal.
        The global moment of inertia is then computed using the parallel axis theoram to sum the contribution
        of each local subshape within the global body container.
        """

        self.J = {}
        FreeCAD.Console.PrintMessage("List of bodies in J: " + str(self.list_of_bodies) + "\n")
        for body_label in self.list_of_bodies:
            J_global_body = 0
            for shape_label in self.parts_of_bodies[body_label]:
                #shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                
                if self.parent_assembly_all[shape_label] != None:
                    shape_obj = DapTools.getAssemblyObjectByLabel(self.doc, self.parent_assembly_all[shape_label] , shape_label)
                else:
                    shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                
                
                if shape_obj.Shape.ShapeType == 'Compound':
                    if len(shape_obj.Shape.Solids)>=1:
                        for i in range(len(shape_obj.Shape.Solids)):
                            J_global_body += self.computeShapeMomentOfInertia(shape_obj.Shape.Solids[i],
                                                                              shape_label,
                                                                              body_label)
                else:
                    J_global_body += self.computeShapeMomentOfInertia(shape_obj.Shape, shape_label, body_label)

            self.J[body_label] = J_global_body
            
            FreeCAD.Console.PrintMessage("Total J: " + str(self.J) + "\n")
            #Iij = 
            
    def computeShapeMomentOfInertia(self, shape_obj, shape_label, body_label):
        # Compound shapes with more than one solid does not have a MatrixOfInertia function
        # Therefore creating recursive function to iteratively loop through subsolids
        Iij = shape_obj.MatrixOfInertia
        density = Units.Quantity(self.material_dictionary[shape_label]["density"]).getValueAs("kg/mm^3")
        #Moment of inertia about axis of orientation (normal of plane)
        J = Iij * self.plane_norm * self.plane_norm  * density * self.scale**2
        #If a part is a subshape of an assemlby, then the part is in the underformed configuration relative
        #to the placement expression link of the assembly 4 object, therefore have to move the 
        #calculated CoG by the same amount that the subassembly was moved by assembly 4
        if self.parent_assembly_all[shape_label] != None:
            parent_assembly_obj = self.doc.getObjectsByLabel(self.parent_assembly_all[shape_label])[0]
            parent_assebly_placement_matrix = parent_assembly_obj.Placement.Matrix
            centre_of_gravity = parent_assebly_placement_matrix * shape_obj.CenterOfMass * self.scale
        else:
            centre_of_gravity = shape_obj.CenterOfMass * self.scale
            
        #Project CoG of shape onto plane and compute distance of projected CoG of current shape to projected
        # body CoG
        CoG_me_proj = self.projectPointOntoPlane(centre_of_gravity)
        CoG_body_proj = self.cog_of_body_projected[body_label]
        #planar_dist_CoG_to_CogBody = ((CoG_me_proj.x - CoG_body_proj.x)**2 + (CoG_me_proj.y - CoG_body_proj.y)**2 
                                #+ (CoG_me_proj.z - CoG_body_proj.z)**2)**0.5
        planar_dist_CoG_to_CogBody = (CoG_body_proj - CoG_me_proj).Length
        
        
        #to convert density back to kg/m^3
        density = density / self.scale**3
        shape_mass = shape_obj.Volume * self.scale**3 * density
        #NOTE: Using parallel axis theoram to compute the moment of inertia of the full body comprised of
        #multiple shapes
        J_body = J + shape_mass * planar_dist_CoG_to_CogBody**2
        return J_body
            
    def centerOfGravityOfCompound(self, compound):
        #Older versions of FreeCAD does not have centerOfGravity and compound shapes do 
        #not have centerOfMass.
        totVol = 0
        CoG = FreeCAD.Vector(0,0,0)
        for solid in compound.Shape.Solids:
            vol = solid.Volume
            totVol += vol
            CoG += solid.CenterOfMass*vol
        CoG /= totVol
        return CoG, totVol
    
    def computeCentreOfGravity(self):
        """  Computes the global centre of mass of each body based on the weighted sum of each subshape centre
        of grabity. """
        self.centre_of_gravity_of_body = {}
        self.cog_of_body_projected = {}
        self.cog_of_body_rotated = {}
        self.total_mass_of_body = {}

        for body_label in self.list_of_bodies:
            total_mass = 0
            centre_of_gravity_global = FreeCAD.Vector(0,0,0)
            for shape_label in self.parts_of_bodies[body_label]:
                #If a part is a subshape of an assemlby, then the part is in the underformed configuration relative
                #to the placement expression link of the assembly 4 object, therefore have to move the 
                #calculated CoG by the same amount that the subassembly was moved by assembly 4
                if self.parent_assembly_all[shape_label] != None:
                    shape_obj = DapTools.getAssemblyObjectByLabel(self.doc, self.parent_assembly_all[shape_label] , shape_label)
                    parent_assembly_obj = self.doc.getObjectsByLabel(self.parent_assembly_all[shape_label])[0]
                    parent_assebly_placement_matrix = parent_assembly_obj.Placement.Matrix
                else:
                    shape_obj = self.doc.getObjectsByLabel(shape_label)[0]
                    parent_assebly_placement_matrix = None
                #NOTE: Older versions of freecad does not have centerOfGravity function, therefore
                #rather using centerOfMass, which does not exist for compound shapes.
                # Therefore performing the check and if body object is a compound shape
                # then perform weighted average of all the subsolid shapes of the compound
                if shape_obj.Shape.ShapeType == 'Compound':
                    if len(shape_obj.Shape.Solids)>=1:
                        centre_of_gravity, volume = self.centerOfGravityOfCompound(shape_obj)
                else:
                    centre_of_gravity = shape_obj.Shape.CenterOfMass
                    volume = shape_obj.Shape.Volume
                
                if parent_assebly_placement_matrix != None:
                    centre_of_gravity = parent_assebly_placement_matrix * centre_of_gravity
                
                volume *= self.scale**3
                centre_of_gravity *= self.scale
                

                #NOTE: Converting density to base units which is mm?
                density = Units.Quantity(self.material_dictionary[shape_label]["density"]).getValueAs("kg/m^3")
                mass = density*volume
                total_mass += mass
                
                centre_of_gravity_global += mass.Value*centre_of_gravity
                
            centre_of_gravity_global /= total_mass
            self.centre_of_gravity_of_body[body_label] =  centre_of_gravity_global
            self.cog_of_body_projected[body_label] = self.projectPointOntoPlane(centre_of_gravity_global)
            self.total_mass_of_body[body_label] = total_mass
            self.cog_of_body_rotated[body_label] = self.global_rotation_matrix * self.cog_of_body_projected[body_label]
        #self.obj.BodiesCoG = self.centre_of_gravity_of_body
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
            body_label = self.list_of_bodies[body_index]
            fid.write("B"+str(i+1)+" = Body_struct()\n")
            fid.write("B"+str(i+1)+".m = " + str(self.total_mass_of_body[body_label]) + "\n")
            fid.write("B"+str(i+1)+".J = " + str(self.J[body_label]) + "\n")
            fid.write("B"+str(i+1)+".r = np.array([[" + str(self.cog_of_body_rotated[body_label].x) + ","
                      + str(self.cog_of_body_rotated[body_label].y) + "]]).T\n")
            fid.write("B"+str(i+1)+".p = " + str(0) + "\n")
            
            fid.write("B"+str(i+1)+".r_d = np.array([[" + 
                      str(self.body_init[body_label]["init_x"]) +
                      ", " +
                      str(self.body_init[body_label]["init_y"]) + "]]).T\n")
            fid.write("B"+str(i+1)+".p_d = " + str(self.body_init[body_label]["init_p"]) + "\n")
            
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
            for key in self.dap_points[i].keys():
                fid.write("P" + str(i+1) + "." + str(key) + " = " + str(self.dap_points[i][key])+"\n")

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
            for key in self.dap_joints[i].keys():
                fid.write("J" + str(i+1) + "." + str(key) + " = " + str(self.dap_joints[i][key])+"\n")

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
            for key in self.dap_forces[i].keys():
                fid.write("F" + str(i+1) + "." + str(key) + " = " + str(self.dap_forces[i][key])+"\n")

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
        for i in range(len(self.dap_funcs)):
            fid.write("F"+str(i+1)+" = Funct_struct()\n")
            for key in self.dap_funcs[i].keys():
                fid.write("F" + str(i+1) + "." + str(key) + " = " + str(self.dap_funcs[i][key])+"\n")

            fid.write("\n")
        
        
        #TODO include writer for functions
        fid.write("\n")
        fid.write('Functs = np.array([[None')
        for i in range(len(self.dap_funcs)):
            fid.write(', F'+str(i+1))
        fid.write("]]).T\n")
    
    def writeUVectors(self):
        file_path = os.path.join(self.folder,"inUvectors.py")
        fid = open(file_path, 'w')
        fid.write('global Uvectors\n')
        for i in range(len(self.dap_uvectors)):
            fid.write("U"+str(i+1)+" = Unit_struct()\n")
            for key in self.dap_uvectors[i].keys():
                fid.write("U" + str(i+1) + "." + str(key) + " = " + str(self.dap_uvectors[i][key])+"\n")

        #TODO include writer for UVectors, needed for translational joints
        fid.write("\n")
        fid.write('Uvectors = np.array([[None')
        for i in range(len(self.dap_uvectors)):
            fid.write(', U'+str(i+1))
        fid.write("]]).T\n")
        

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
        

        pythonCommand = "python3 " + str(dap_solver) + " " + str(self.folder)

        
        #from PySide.QtCore import QProcess
        #process = QProcess()
        #self.process = QtCore.QProcess()
        #self.process.finished.connect(self.onFinished)
        
        FreeCAD.Console.PrintMessage("DAP solver started.\n")
        
        #self.process.start("python3",[str(dap_solver), str(self.folder)])
        #self.process.start(pythonCommand)
        ##proc.waitForStarted()
        #TODO need to overwrite waitForFinished to latch on to the output
        #self.process.waitForFinished()
        #output = self.process.readAllStandardOutput()
        #FreeCAD.Console.PrintMessage(output)
        import subprocess
        import sys
        #import os
        #result = subprocess.run(["python", dap_solver, self.folder])
        #os.system(dap_solver + " " + str(self.folder))
        import dap_temp_temp
        dap_temp_temp.folder = self.folder
        dap_temp_temp.readInputFiles()
        dap_temp_temp.initialize()
        dap_temp_temp.t_initial = self.t_initial
        dap_temp_temp.dt = self.reporting_time
        dap_temp_temp.t_final = self.t_final
        dap_temp_temp.solve()
        dap_temp_temp.writeOutputs()
        
        
        FreeCAD.Console.PrintMessage("Was the solve step success: " + str(dap_temp_temp.solution_success) + "\n")
        FreeCAD.Console.PrintMessage("write success: " + str(dap_temp_temp.write_success) + "\n")
        #FreeCAD.Console.PrintMessage("Python runnable" + sys.executable + "\n")
        #result = subprocess.run([sys.executable, dap_solver, self.folder])
        #FreeCAD.Console.PrintMessage(result)
        self.loadResults()
        
    def onFinished(self,  exitCode,  exitStatus):
        if exitCode == 0:
            FreeCAD.Console.PrintMessage("Solver completed Succesfully \n")
            self.loadResults()
            self.resultsAvailable = True
        else:
            FreeCAD.Console.PrintError("Solver Failed: error codes not yet included (in the TODO list)\n")
        
    def loadResults(self):
        #results = os.path.join(self.folder, "dapResults.npy")
        self.dapResults = True
        
        #read body CoG positions
        fid_DapBodyPositions = open(os.path.join(self.folder,"DapBodyPositions"))
        Bodies_r = []
        Bodies_p = []
        reported_times = []
        DapBodyPositions_lines = fid_DapBodyPositions.readlines()
        for line in DapBodyPositions_lines[1::]:
            items = line.split()
            r = []
            p = []
            reported_times.append(float(items[0]))
            for i in range(len(self.moving_bodies)):
                x = float(items[i*3+1])
                y = float(items[i*3+2])
                phi = float(items[i*3+3])
                r.append([x,y])
                p.append(phi)
            Bodies_r.append(r)
            Bodies_p.append(p)
        fid_DapBodyPositions.close()

        #read body CoG velocities
        fid = open(os.path.join(self.folder,"DapBodyVelocities"))
        Bodies_r_d = []
        Bodies_p_d = []
        lines = fid.readlines()
        for line in lines[1::]:
            items = line.split()
            r = []
            p = []
            for i in range(len(self.moving_bodies)):
                x = float(items[i*3+1])
                y = float(items[i*3+2])
                phi = float(items[i*3+3])
                r.append([x,y])
                p.append(phi)
            Bodies_r_d.append(r)
            Bodies_p_d.append(p)
        fid.close()
        
        #read body CoG accelerations
        fid = open(os.path.join(self.folder,"DapBodyAccelerations"))
        Bodies_r_d_d = []
        Bodies_p_d_d = []
        lines = fid.readlines()
        for line in lines[1::]:
            items = line.split()
            r = []
            p = []
            for i in range(len(self.moving_bodies)):
                x = float(items[i*3+1])
                y = float(items[i*3+2])
                phi = float(items[i*3+3])
                r.append([x,y])
                p.append(phi)
            Bodies_r_d_d.append(r)
            Bodies_p_d_d.append(p)
        fid.close()
        
        #read point co-ordinate
        fid = open(os.path.join(self.folder,"DapPointsPositions"))
        Points_r = []
        lines = fid.readlines()
        for line in lines[1::]:
            items = line.split()
            r = []
            for i in range(len(self.dap_points)):
                x = float(items[i*2+1])
                y = float(items[i*2+2])
                r.append([x,y])
            Points_r.append(r)
        fid.close()
        
        #read point co-ordinate velocities
        fid = open(os.path.join(self.folder,"DapPointsVelocities"))
        Points_r_d = []
        lines = fid.readlines()
        for line in lines[1::]:
            items = line.split()
            r = []
            for i in range(len(self.dap_points)):
                x = float(items[i*2+1])
                y = float(items[i*2+2])
                r.append([x,y])
            Points_r_d.append(r)
        fid.close()
        
        #read body energies
        fid = open(os.path.join(self.folder,"DapSystemEnergy"))
        #Points_r_d = []
        kinetic = []
        potential = []
        total = []
        lines = fid.readlines()
        for line in lines[1::]:
            items = line.split()

            kinetic.append(float(items[1]))
            potential.append(float(items[2]))
            total.append(float(items[3]))
        fid.close()

        
        self.obj.DapResults = self.dapResults
        self.obj.Bodies_r = Bodies_r
        self.obj.Bodies_p = Bodies_p
        self.obj.Bodies_r_d = Bodies_r_d
        self.obj.Bodies_p_d = Bodies_p_d
        self.obj.Bodies_r_d_d = Bodies_r_d_d
        self.obj.Bodies_p_d_d = Bodies_p_d_d
        self.obj.Points_r = Points_r
        self.obj.Points_r_d = Points_r_d
        self.obj.kinetic_energy = kinetic
        self.obj.potential_energy = potential
        self.obj.total_energy = total
        self.obj.ReportedTimes = reported_times
        
        
        #DapBodyAccelerations
        #DapBodyPositions
        #DapBodyVelocities
        #DapPointsPositions
        #DapPointsVelocities
        #DapSystemEnergy
        
        
        #import pickle
        #with open(os.path.join(self.folder,"Bodies_r"), "rb") as fp:   #Pickling
            #self.obj.Bodies_r = pickle.load(fp)
        #with open(os.path.join(self.folder,"Bodies_p"), "rb") as fp:   #Pickling
            #self.obj.Bodies_p = pickle.load(fp)
        #with open(os.path.join(self.folder,"Bodies_r_d"), "rb") as fp:   #Pickling
            #self.obj.Bodies_r_d = pickle.load(fp)
        #with open(os.path.join(self.folder,"Bodies_p_d"), "rb") as fp:   #Pickling
            #self.obj.Bodies_p_d = pickle.load(fp)
        
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
