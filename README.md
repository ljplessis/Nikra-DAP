# FreeCAD Nikra-DAP WorkBench

The FreeCAD Nikra-DAP WorkBench is a planar multibody dynamics workbench that is based on Prof. Nikravesh's DAP solver. 


# Installation

This workbench can be installed through the **Addon Manager** in FreeCAD ( menu **Tools > Addon Manager**.) This workbench can be utlisied in the stable release (0.19) as well as the unstable releases (0.20)

In order for this workbench to work correctly. **FreeCAD Plot** as well as **Assembly 4** should also be installed on your computer through the addon manager. 

*Why Assembly 4?* 

FreeCAD has been infamously known for its topological naming issue. Meaning that whenever you have an assembly opened in Assembly 2, you could not edit an indidivual part geometry without the assembly breaking and forcing you to start over.

**Assembly 4** fixes this issue as you can make edits to your part geometries and it will update accordingly. This is due to the usage of a local coorindate system (LCS) feature that allows you to attach an LCS to a body and use this LCS to create mates with other bodies. In addition to this, **Assembly 4**  

*Nikra-DAP* was designed with **Assembly 4** in mind and makes use of the LCS when creating a DAP mechanism. 

*However*, *Nikra-DAP* does still work well with Assembly 2 files. It is recommended however that mechnanism created in **Assembly 4** are used. 


# Basic Overview 

In order to utilise the Nikra-DAP solver to solve planar dynamic problems. Several analysis parameters needs to be defined. 

These parameters are defined as follows: 

* DapBody: A single body that forms part of a multibody system. The equations of motion are then constructed for this body by using the body-coordinate method. (Nikravesh, 2019) These can be defined as either ground or moving and intial conditions can be assigned to them.

* DapJoint: This defines the Degrees of Freedom between several bodies or between a body and ground. This can either be revolute or linear translation. 

* DapForce:  Forces such as gravity, a linear spring, linear damper, rotational (torsional) spring and rotational damper are options and its placement in the mechanism can also be selected. **(This makes use of the LCS assigned to a body as well as the body itself)** 

* DapMaterial: This defines the material properties for each DapBody. You can also manually insert a density if your material is not shown in the list. 

*DapSolver: Allows you to select the plane of motion and also the time step. 









