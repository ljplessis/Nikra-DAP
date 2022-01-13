#TODO add license
#NOTE Some of these functions come from CfdOF, need to give credit

import FreeCAD
import os

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

def get_module_path():
    """ Returns the current Dap module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    """
    return os.path.dirname(__file__)


def indexOrDefault(list, findItem, defaultIndex):
    """ Look for findItem in list, and return defaultIndex if not found """
    try:
        return list.index(findItem)
    except ValueError:
        return defaultIndex
