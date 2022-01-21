import FreeCAD 
import math


def add(first, other):
    """add(Vector,Vector) - adds two vectors"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return FreeCAD.Vector(first.x+other.x, first.y+other.y, first.z+other.z)
 
def sub(first, other): 
    """sub(Vector,Vector) - subtracts second vector from first one"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return FreeCAD.Vector(other.x-first.x, other.y-first.y, other.z-first.z)
 
def scale(first,scalar):
    """scale(Vector,Float) - scales (multiplies) a vector by a factor"""
    if isinstance(first,FreeCAD.Vector):
        return FreeCAD.Vector(first.x*scalar, first.y*scalar, first.z*scalar)
 
def length(first):
    """lengh(Vector) - gives vector length"""
    if isinstance(first,FreeCAD.Vector):
        return math.sqrt((first.x**2) + (first.y**2) + (first.z**2))
 
def dist(first, other):
    """dist(Vector,Vector) - returns the distance between both points/vectors"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return length(sub(first,other))
 
def normalized(first):
    """normalized(Vector) - returns a unit vector"""
    if isinstance(first,FreeCAD.Vector):
        l=length(first)
        return FreeCAD.Vector(first.x/l, first.y/l, first.z/l)
 
def dotproduct(first, other):
    """dotproduct(Vector,Vector) - returns the dot product of both vectors"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return (first.x*other.x + first.y*other.y + first.z*other.z)
 
def crossproduct(first, other=FreeCAD.Vector(0,0,1)):
    """crossproduct(Vector,Vector) - returns the cross product of both vectors. 
    If only one is specified, cross product is made with vertical axis, thus returning its perpendicular in XY plane"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return FreeCAD.Vector(first.y*other.z - first.z*other.y, first.z*other.x - first.x*other.z, first.x*other.y - first.y*other.x)
 
def angle(first, other=FreeCAD.Vector(1,0,0)):
    """angle(Vector,Vector) - returns the angle in radians between the two vectors. 
    If only one is given, angle is between the vector and the horizontal East direction"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return math.acos(dotproduct(normalized(first),normalized(other)))
 
def project(first, other):
    """project(Vector,Vector): projects the first vector onto the second one"""
    if isinstance(first,FreeCAD.Vector) and isinstance(other,FreeCAD.Vector):
        return scale(other, dotproduct(first,other)/dotproduct(other,other))