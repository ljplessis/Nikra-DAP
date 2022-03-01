# ************************************************************************************
# *                                                                                  *
# *   Copyright (c) 2022 Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>            *
# *   Copyright (c) 2022 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>                   *
# *   Copyright (c) 2022 Johan Heyns (EX-MENTE) <jheyns@ex-mente.co.za>              *
# *   Copyright (c) 2022 Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>   *
# *   Copyright (c) 2022 Dewald Hattingh (UP) <u17082006@tuks.co.za>                 *
# *   Copyright (c) 2022 Varnu Govender (UP) <govender.v@tuks.co.za>                 *
# *                                                                                  *
# *   This program is free software; you can redistribute it and/or modify           *
# *   it under the terms of the GNU Lesser General Public License (LGPL)             *
# *   as published by the Free Software Foundation; either version 2 of              *
# *   the License, or (at your option) any later version.                            *               
# *   for detail see the LICENCE text file.                                          *
# *                                                                                  *
# *   This program is distributed in the hope that it will be useful,                *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of                 *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  *
# *   GNU Library General Public License for more details.                           *
# *                                                                                  *
# *   You should have received a copy of the GNU Library General Public              *   
# *   License along with this program; if not, write to the Free Software            *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307           *
# *   USA                                                                            *
# *_________________________________________________________________________________ *        
# *                                                                                  *
# *     Nikra-DAP FreeCAD WorkBench (c) 2022:                                        *
# *        - Please refer to the Documentation and README                            *
# *          for more information regarding this WorkBench and its usage.            *
# *                                                                                  *
# *     Author(s) of this file:                                                      *                         
# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
# *        -  Dewald Hattingh (UP) <u17082006@tuks.co.za>                            *
# *        -  Varnu Govender (UP) <govender.v@tuks.co.za>                            *
# *        -  Code snippets adapted from CfdOF Workbench                             *
# ************************************************************************************

#NOTE Some of these functions come from CfdOF, need to give credit

import FreeCAD
import os
from FreeCAD import Units

def setActiveAnalysis(analysis):
    from DapAnalysis import _DapAnalysis
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, _DapAnalysis):
            obj.IsActiveAnalysis = False

    analysis.IsActiveAnalysis = True


def getActiveAnalysis():
    from DapAnalysis import _DapAnalysis
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, _DapAnalysis):
            if obj.IsActiveAnalysis:
                return obj
    return None



def getListOfSolidsFromShape(obj, shape_label_list=[], parent_object = None, parent_assembly = {}):
    """ Recursively loops through assemblies or shape object to find all the
    sub shapes
    input:
        obj: object, such as assembly container, part, body
    returns: 
        shape_label_list: list to the labels of objects contained within obj """
    #parent_assembly = {}
    if hasattr(obj, 'Shape'):
        solids = obj.Shape.Solids
        if len(solids) == 1:
            shape_label_list.append(obj.Label)
            if parent_object == None:
                parent_assembly[obj.Label] = None
            else:
                parent_assembly[obj.Label] = parent_object.Label
        elif len(solids)>1:
            #if hasattr(obj, "Group"):
            if hasattr(obj, "Type"):
                if obj.Type == "Assembly":
                    #This applies to assemlby 4 assemlbies
                    #TODO add in a formal checker for assemblies
                    for sub_object in obj.Group:
                        getListOfSolidsFromShape(sub_object, shape_label_list, obj, parent_assembly)
            elif obj.Shape.ShapeType == 'Compound':
                shape_label_list.append(obj.Label)
                if parent_object == None:
                    parent_assembly[obj.Label] = None
                else:
                    parent_assembly[obj.Label] = parent_object.Label

    return shape_label_list, parent_assembly

def getSolidsFromAllShapes(doc):
    """ Function loops through all defined bodies, and return the list of shapes making up each body, as 
    well as return the parent assemlby for each sub part. If the subpart does not have a parent assembly then
    it is defined as None. """
    body_labels = getListOfBodyLabels()
    parts_shape_list_all = {}
    parent_assembly_all = {}
    if len(body_labels):
        for i in range(len(body_labels)):
            selection_object = doc.getObjectsByLabel(body_labels[i])[0]
            list_of_parts = selection_object.References
            for current_body_label in list_of_parts:
                obj = doc.getObjectsByLabel(current_body_label)[0]
                shape_label_list, parent_assembly = getListOfSolidsFromShape(obj, [])
                parts_shape_list_all[current_body_label] = shape_label_list
                parent_assembly_all.update(parent_assembly)
    return parts_shape_list_all, parent_assembly_all
    

def getAssemblyObjectByLabel(doc, parent_assembly_label, part_label):
    parent_assembly_obj = doc.getObjectsByLabel(parent_assembly_label)[0]
    for sub_object in parent_assembly_obj.Group:
        if sub_object.Label == part_label:
            return sub_object
    return None

def addObjectProperty(obj, prop, init_val, type, *args):
    """ Call addProperty on the object if it does not yet exist """
    added = False
    if prop not in obj.PropertiesList:
        added = obj.addProperty(type, prop, *args)
    if type == "App::PropertyQuantity":
        # Set the unit so that the quantity will be accepted
        # Has to be repeated on load as unit gets lost
        setattr(obj, prop, Units.Unit(init_val))
    if added:
        setattr(obj, prop, init_val)
        return True
    else:
        return False

def getListOfBodyLabels():
    body_labels = []
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapBody" in i.Name:
                body_labels.append(i.Label)
    return body_labels


def getListOfBodyObjects():
    body_object = []
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapBody" in i.Name:
                body_object.append(i)
    return body_object


def getListOfMovingBodies(list_of_body_labels, solver_document):
    moving_bodies = []
    
    #for body in self.body_objects:
    for i in range(len(list_of_body_labels)):
        body_object = solver_document.getObjectsByLabel(list_of_body_labels[i])[0]
        if body_object.BodyType == "Moving":
            moving_bodies.append(list_of_body_labels[i])
    return moving_bodies

def getListOfBodyReferences():
    body_references = []
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapBody" in i.Name:
                body_references = body_references + i.References
    return body_references

def getListOfForces(): #Mod
    forces = []
    active_analysis = getActiveAnalysis()
    for j in active_analysis.Group:
        if "DapForce" in j.Name:
            forces.append(j.ForceTypes)
    return forces


def getMaterialObject():
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapMaterial" in i.Name:
                return i
    return None

def getSolverObject():
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapSolver" in i.Name:
                return i
    return None

def getForcesObjects():
    force_objects = []
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapForce" in i.Name:
                force_objects.append(i)
    return force_objects

def getListOfJointObjects():
    joints = []
    active_analysis = getActiveAnalysis()
    for i in active_analysis.Group:
            if "DapRelativeMovement" in i.Name:
                joints.append(i)
    return joints

def get_module_path():
    """ Returns the current Dap module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    """
    return os.path.dirname(__file__)

def gravityChecker():
    counter=0
    active_analysis=getActiveAnalysis()
    for i in active_analysis.Group:
        if "DapForce" in i.Name:
            if i.ForceTypes == "Gravity":
                counter+=1
    if counter>1:
        return True 
            
    else:
        return False
         

    

def indexOrDefault(list, findItem, defaultIndex):
    """ Look for findItem in list, and return defaultIndex if not found """
    try:
        return list.index(findItem)
    except ValueError:
        return defaultIndex


def setQuantity(inputField, quantity):
    """ Set the quantity (quantity object or unlocalised string) into the inputField correctly """
    # Must set in the correctly localised value as the user would enter it.
    # A bit painful because the python locale settings seem to be based on language,
    # not input settings as the FreeCAD settings are. So can't use that; hence
    # this rather roundabout way involving the UserString of Quantity
    q = Units.Quantity(quantity)
    #unit = Units.schemaTranslate(q, Units.getSchema())[2]
    #q = q.getValueAs(unit)
    #q = Units.Quantity(unit_quantity[0] + unit_quantity[2])
    # Avoid any truncation
    if isinstance(q.Format, tuple):  # Backward compat
        q.Format = (12, 'e')
    else:
        q.Format = {'Precision': 12, 'NumberFormat': 'e', 'Denominator': q.Format['Denominator']}
    inputField.setProperty("quantityString", q.UserString)


def getQuantity(inputField):
    """ Get the quantity as an unlocalised string from an inputField """
    q = inputField.property("quantity")
    return str(q)


def projectPointOntoPlane(plane_norm, point, plane_origin = FreeCAD.Vector(0,0,0)):
    """ Projects a given vector onto the plane defined by the norm of the plane, passing through the (0,0,0) """
    projected_point = point - (plane_norm * (point - plane_origin)) * plane_norm
    
    #FreeCAD.Console.PrintMessage("Projected point " + str(point) + ": " + str(projected_point) + "\n")
    return projected_point
