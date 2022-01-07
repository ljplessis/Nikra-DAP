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
