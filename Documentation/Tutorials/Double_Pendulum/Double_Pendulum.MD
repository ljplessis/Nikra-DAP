# Double Pendulum 
This tutorial will show you how to use the Nikra-DAP FreeCAD WorkBench to solve a double pendulum dynamics problem. Please refer to the README for a basic run-down on all features within Nikra-DAP.

<br/>

# Double Pendulum tutorial

## Prerequisites 
In order to progress further with this tutorial, you need to have: 
1. Nikra-DAP WorkBench installed (refer to the **Readme** for further information on installation)
2. FreeCAD Plot WorkBench Installed (available in **Addon Manager**)
3. Assembly 4 WorkBench Installed (available in **Addon Manager**)

## Initial Steps 

An assembly file for the double pendulum has been made available for purposes of this tutorial. If you are familiar with Assembly 4, you can recreate this assembly, *the steps for this tutorial will not change* 

The assembly files can be found in the **FreeCAD Tutorial Files** folder in **Documentation**, you only need to open the FreeCAD Assembly file. (They have been marked with **OPEN**)

## Opening the WorkBench

Depending on your FreeCAD workflow, you might open your workbenches differently. If you have your workbench panel open in your view finder, you should be able to find the Nikra-DAP WorkBench easily. 

![Opening the WorkBench](./Illustrations/1.png)

## Setting the parameters

### Body Selection 

When working with an assembly, you need to select the bodies that need to remain grounded (stationary) as well as select the moving bodies. In our case, the double pendulum is a multi body mechanism and each individual pendulum would need to be chosen separately as they move independently of each other. 

Firstly, open a new Dap Analysis container and select the DapBody selector. 

![Selecting the DapBody Selector](./Illustrations/2.png)

Once the menu has been opened, you can now select the body type and add bodies to your 'Parts list.' If you have selected a moving part, you can also specify initial conditions. If changes has not been made, it will default to zero. 

You can select **moving** as a body type, for now, lets leave initial conditions unchanged. 

![Initial selection of body type](./Illustrations/3.png)

**NB!!** This step is crucial, because the orientations of bodies has now been altered through the Assembly 4 workbench. It is recommended that you make body selections in the *model tree view*

This is illustrated below: 

1. Switch to the model tree view, making selections from the tree view and not the graphic display will ensure that you select the body in the correct formation. 
2. Select the body 
3. Switch back to the DapBody task panel.
4. Click *Add*
5. The body will show up on the parts list, it should also highlight on screen in a different colour. 
6. Click *Ok* or hit *Enter* 

![Selecting the body](./Illustrations/4.png)
![Selecting the body](./Illustrations/5.png)

You will notice that the body is highlighted and you can use this to confirm if you have selected the body correctly. Once you have clicked *Ok* you can hover over the DAPBody container and the part will highlight. 

You would need to complete this step twice, for each individual body as shown below:

Every time you need to define a new Dap Body, Joint or Force, you would need to open a new 'container' for that entity:

![Selecting the DapBody Selector](./Illustrations/6.png)

You can now redo the steps as shown:

![Selecting the body](./Illustrations/7.png)
![Selecting the body](./Illustrations/8.png)

**You have now assigned the DapBodies successfully!!**

### Joint Selection 

Selecting DapJoints, or the relative movement between bodies is up next. 

In our case, we need to define relative motion between the first pendulum (DapBody) that will rotate about a fixed point as well as the second pendulum (DapBody001) that will be attached to the first one and also rotate about an axis (in this case, we have defined a LCS that is concentric with the centers of both holes).

We need to use the *'revolute'* joint in both cases. The selection of a revolute joint works with the 'One point and two bodies' principle.

If you have a look at your tree view as well as the graphic display, you will notice that in assembly 4, we have assigned a local coordinate system (LCS) to the top of the first pendulum as well as another one that is defined between both pendulums. **This will act as points about which both pendulums will rotate**

Open the joint selection panel to do this: 

![Selecting the body](./Illustrations/9'.png)

**Due to the fact that multiple LCS's were utilised to complete this assembly, we would need to make use of the *model tree view* to select the LCS points to create relative motion**

Once again, relative movement would need to be assigned twice as there are two points of rotation in this mechanism. 

The steps are as follows: 

A. Choose *rotation* in the drop down box. (This isn't always necessary as the rotation joint is active by default)

1. Switch to the *model tree view*

![Selecting the body](./Illustrations/10'.png)

2. Select LCS_Ground in the tree view
3. Switch back to the *DapJoint task panel* 
4. Click *add point*, this will also highlight the LCS to make sure you have selected the correct one. 
5. In this case, you want the first pendulum (DapBody) to rotate around the LCS_Ground, hence one body can be ground and the other can be the DapBody. 
6. Click *Ok* or hit *Enter*

![Selecting the body](./Illustrations/9.png)
![Selecting the body](./Illustrations/10.png)

**NB! You can select the bodies in any order, Body 1 can be the DapBody and Body 2 can be ground, this should not affect the results. In addition to this, you can also select the LCS in the model tree view, it would be better to make selections in the model tree view but for this case, it was not necessary**

You will notice that a rounded arrow will show up. If this shows up at the correct place, you have chosen the revolute joint/relative movement correctly.

This needs to be done one more time for the joint between the two pendulums. 

You will follow the same steps. However, you will choose LCS_link2 in the model tree view and choose both DapBodies in the body selection menu. 

This is illustrated as follows: 

Every time you need to define a new Dap Body, Joint or Force, you would need to open a new 'container' for that entity:

![Selecting the body](./Illustrations/9'.png)

You can now redo the steps as shown:

![Selecting the body](./Illustrations/11'.png)
![Selecting the body](./Illustrations/11.png)
![Selecting the body](./Illustrations/12.png)

If you have two rounded arrows rotating about the two joints, you have attached relative movement to the mechanism correctly. 

### Material Selection 

Selecting DapMaterials is also crucial as the density of materials is taken into account when computing the Moment of Inertia matrix. 

You are welcome to also select your own density if your desired material is not in the drop down list. Materials will have to be assigned to each pendulum.  

Open the material selection panel: 

![Selecting the body](./Illustrations/13'.png)


1. Select the DapBody for the material selection
2. Use the drop down menu to select the material. In this case, we will use *Steel-1C22*

Use the drop down menu shown with ***1*** and select DapBody001, you can then assign *Steel-1C22* to that DapBody as well.

3. Click *Ok* or hit *Enter*

![Selecting the body](./Illustrations/13.png)

**NB!! Remember to do this for each DapBody that you have defined, as a different material might be attached to each DapBody.**

## Force Selection 

A variety of forces can be created in Nikra-DAP. For our double pendulum we only need a gravitational force. 

Open the force selection panel: 

![Selecting the body](./Illustrations/15'.png)

In the *Force Type* drop down menu, you can select gravity and click *Ok* or hit *Enter* 

![Selecting the body](./Illustrations/15.png)

*Note: if you want to play around, you can alter the gravity vector to change the direction in which gravity acts* 

### Running the solver 

Two more steps need to be completed before we can solve this double pendulum problem, we need to define the plane of motion as well as define the time steps. 

Open the solver panel: 

![Selecting the body](./Illustrations/16'.png)

A wide variety of options are available for the plane of motion. You are welcome to choose the *X-Y Plane* as the plane of motion. 

However, to illustrate how the 'Master-Sketch' can be selected to define the plane of motion, the following steps need to be followed: 

You can first select a save directory, its best to select the folder at which the FreeCAD document is saved.

1. In the drop down menu, choose *custom plane* 
2. The master sketch is technically an 'Object', hence in this drop down menu you need to choose *object selection*
3. Switch to the *model tree view*
4. Find the 'Body_MS...' document and then select the sketch that is contained there. This is the **Master-Sketch** used in Assembly 4
5. Switch back to the *DapSolver task panel*
6. Click *Select*
7. You can define the time steps here.
8. Click Solve

![Selecting the body](./Illustrations/16.png)
![Selecting the body](./Illustrations/18.png)

Depending on your system specifications as well as the reporting time entered, the solve time will vary. Once it is completed, you will see the following message in the *report console*:

![Selecting the body](./Illustrations/20.png)

9. Click *Ok* or hit *Enter*

### Viewing the animation

Open the animation panel:

![Selecting the body](./Illustrations/21'.png)

Here you can play the animation and also adjust the speed. 

Here is an example of how it should look: 

![Selecting the body](./Illustrations/21.gif)

### Plotting 

Open the plotting selection panel: 

![Selecting the body](./Illustrations/22'.png)

You can plot several different plots and you can view those both in orthonormal coordinates or 3D coordinates. 

For example, let us view a 2D sketch of the velocity of our second pendulum (DapBody001):

1. You can select *velocity* in the plotting drop down menu, here you can also see what other plots can be generated for this mechanism. 
2. Select your coordinate system, in our case we will use the orthonormal coordinate system. 
3. You can select which bodies in particular that you want to analyse. Select *DapBody001* from the drop down menu and click *add*. 
4. Click on *plot* and a new document with your generated plot will be opened. With each new plot you generate a new document will be opened. In this case, because we have two components of velocity, it has been plotted individually in the X & Y directions. 

![Selecting the body](./Illustrations/22.png)

Once the plot has been generated, you will be able to use several controls to interact with the plot. **If you are familiar with how Juypter NoteBook plotting works, the controls are identical to that.**

![Selecting the body](./Illustrations/23.png)
![Selecting the body](./Illustrations/24.png)

You are welcome to tinker with your Dap Analysis to explore the other options that are available to you. 

