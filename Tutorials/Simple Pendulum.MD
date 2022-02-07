# Simple Pendulum 
This tutorial will show you how to use the Nikra-DAP FreeCAD WorkBench to solve a simple pendulum dynamics problem. 

# Basic Overview 

The FreeCAD Nikra-DAP WorkBench is a planar multibody dynamics workbench that is based on Prof. Nikravesh's DAP solver. 

In order to utilise the Nikra-DAP solver to solve planar dynamic problems. Several analysis parameters needs to be defined. 

These parameters are defined as follows: 

* DapBody: A single body that forms part of a multibody system. The equations of motion are then constructed for this body by using the body-coordinate method. (Nikravesh, 2019) These can be defined as either ground or moving and intial conditions can be assigned to them.

* DapJoint: This defines the Degrees of Freedom between several bodies or between a body and ground. This can either be revolute or linear translation. 

* DapForce:  Forces such as gravity, a linear spring, linear damper, rotational (torsional) spring and rotational damper are options and its placement in the mechanism can also be selected. **(This makes use of the LCS assigned to a body as well as the body itself)** 

* DapMaterial: This defines the material properties for each DapBody. You can also manually insert a density if your material is not shown in the list. 

* DapSolver: Allows you to select the plane of motion and also the time step. The plane of motion can be one of the cartesian planes, a plane auto-generated from a selected object. From an Assembly 4 standpoint, by using the object selection feature, you can select the master sketch and use the plane of motion defined within the master sketch. 

* DapAnimate: Once the solver has completed, you can then view an animation of the DAP Mechanism. 

* DapPlot: Several plots can be generated for each of the bodies. These plots include: postion, velocity, a path trace as well as energies. These can be plotted in orthonormal co-ordinates or 3D co-coordinates. 

# Simple Pendulum tutorial 

## Prerequisites 
In order to progress further with this tutorial, you need to have: 
1. Nikra-DAP WorkBench installed ( refer to the **Readme** for further information on installation)
2. FreeCAD Plot WorkBench Installed (availible in **Addon Manager**)
3. Assembly 4 WorkBench Installed (availible in **Addon Manager**)


