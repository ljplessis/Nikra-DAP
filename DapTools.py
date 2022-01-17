#TODO add license

#TODO TODO Add Johan Heyns and Oliver Oxtoby to the Copyright in the license for this file
# copy and pasted code from CfdOF workbench

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


def getListOfSolidsFromShape(obj, shape_label_list=[]):
    """ Recursively loops through assemblies or shape object to find all the
    sub shapes
    input:
        obj: object, such as assembly container, part, body
    returns: 
        shape_label_list: list to the labels of objects contained within obj """
    
    if hasattr(obj, 'Shape'):
        solids = obj.Shape.Solids
        if len(solids) == 1:
            shape_label_list.append(obj.Label)
        elif len(solids)>1:
            if hasattr(obj, "Group"):
                for sub_object in obj.Group:
                    getListOfSolidsFromShape(sub_object, shape_label_list)
    else:
        if hasattr(obj, "Shape"):
            solids = obj.Shape.Solids
            if len(solids)>0:
                shape_label_list = [obj.Label]
    return shape_label_list

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
