 
##-------------------------------------------------%%% Imports
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
import os
import sys
# %matplotlib qt5 (For Jupyter- Notebook --> .ipynb)

##-------------------------------------------------%%% Include global variables 
global Bodies, nB, nB3, nB6      
global Points, nP, Points_anim, nPanim, nPtot
global Uvectors, nU 
global Joints, nJ, nConst
global Forces, nF
global M_array, M_inv_array
global Functs, nFc
global ZZ, redund, cfriction
global num, D, Dt, Lambda 
global xmin, xmax, ymin, ymax
global showtime, t10
global flags, pen_d0



from structures import Body_struct, Force_struct, Joint_struct, Point_struct, Unit_struct, Funct_struct




#TODO clean up dap code. build into proper class structure
#for now just getting it to work within the workbench

################################################################
#
#ANALYSIS
#
################################################################
def analysis(t, u):
    global Bodies, nB, nB3, nB6      
    global Points, nP, Points_anim, nPanim, nPtot
    global Uvectors, nU 
    global Joints, nJ, nConst
    global Forces, nF
    global M_array, M_inv_array
    global Functs, nFc
    global ZZ, redund, cfriction
    global num, D, Dt, Lambda 
    global xmin, xmax, ymin, ymax
    global showtime, t10
    global flags, pen_d0
    global M_array_, M_inv_array_
    
    M_array_     = np.atleast_2d(M_array[1:3*(nB-1)+1,0]).T
    M_inv_array_ = np.atleast_2d(M_inv_array[1:3*(nB-1)+1,0]).T

    u_to_Bodies(u)
    Update_Position()
    Update_Velocity()
    
    h_a  = Force_array(t)
    h_a_ = np.atleast_2d(h_a[1:3*(nB-1)+1,0]).T
    
    if nConst == 0:
        c_dd = M_inv_array_ * h_a_
    else:
        D  = Jacobian(t)
        D_ = D[:,0:3*(nB-1)]
        
        rhsA = RHSAcc(t)
        
        DMD1   = np.concatenate( (np.diag(M_array_[:,0]), -D_.T),axis=1 )
        DMD2   = np.concatenate( (D_, np.zeros((nConst,nConst)) ),axis=1 )
        DMD    = np.concatenate( (DMD1, DMD2), axis=0 )
        rhs    = np.concatenate( (h_a_, rhsA), axis=0 )
        sol    = np.linalg.solve(DMD, rhs)
        c_dd   = sol[0:3*(nB-1)]
        Lambda = sol[3*(nB-1):len(sol)]
    
    for Bi in range(1,nB):
        ir = Bodies[Bi,0].irc
        i2 = ir + 1
        i3 = i2 + 1
        Bodies[Bi,0].r_dd = c_dd[ir-1:i2]
        Bodies[Bi,0].p_dd = c_dd[i3-1]
    
    u_d = Bodies_to_u_d()

    global num
    num = num + 1
    
    if showtime == 1:
        if np.mod(t10, 100) == 0:
            print(t)
           
        t10 = t10 + 1


    return np.concatenate((u_d), axis=None)



################################################################
#
# Constraints
#
################################################################
 
def Constraints():
    global nConst, nJ

    phi = np.zeros(nConst,1)
    
    for Ji in range(1,nJ):
        if Joints[Ji].type == 'rev':
            f=C_rev(Ji)
             
        if Joints[Ji].type == 'tran':
            f=C_tran(Ji)
            
        if Joints[Ji].type == 'rev_rev':
            f=C_rev_rev(Ji)
            
        if Joints[Ji].type == 'rev_tran':
            f=C_rev_tran(Ji)
            
        if Joints[Ji].type == 'rigid':
            f=C_rigid(Ji)
            
        if Joints[Ji].type == 'disc':
            f=C_disc(Ji)
            
        if Joints[Ji].type == 'rel_rot':  
            f=C_rel_rot(Ji)
            
        if Joints[Ji].type == 'rel_tran':
            f=C_rel_tran(Ji)
        
        rs = Joints[Ji].rows -1 
        re = Joints[Ji].rowe
        phi[rs:re] = f


################################################################
#
# Forces
#
################################################################
 

#%% Forces
#%%% Contact
def Contact(Ci, Pi, Bi, k, e, Mi):
    global flags
    global Bodies
    global flags_

    flags = np.zeros( (10,1) )
    pen = -Points[Pi,0].rP[1,0] 
    
    if pen > 0:
        pen_d = -Points[Pi,0].rP_d[1,0]
        
        if flags[Ci,0] == 0:
            pen_d0[Ci,0] = pen_d
            flags[Ci,0] = 1
        
        if Mi == 1:
            fy = Contact_LN(pen, pen_d, pen_d0[Ci,0], k, e) # penetration force
        else:
            fy = Contact_FM(pen, pen_d, pen_d0[Ci,0], k, e) # penetration force
        
        fsd = np.array([[0],[fy]])                
        Bodies[Bi,0].f = Bodies[Bi,0].f + fsd
        Bodies[Bi,0].n = Bodies[Bi,0].n + Points[Pi,0].sP_r.T @ fsd
        
    else:
        flags[Ci,0] = 0
        
    return None

#%%% Contact_FM
def Contact_FM(delta, deld, deld0, K, e):                 #Contact force model Flores-Machado-Silva-Martins
    fn = K*(delta**1.5)*(1 + 8*(1 - e)*deld/(5*e*deld0))
    return fn

#%%% Contatc_LN
def Contact_LN(delta, deld, deld0, K, e):                 # Contact force model Lankarani-Nikravesh
    fn = K*(delta**1.5)*(1 + 3*(1 - np.e**2)*deld/(4*deld0))
    return fn

#%%% Friction_A
def Friction_A(mu_s, mu_d, v_s, p, k_t, v, fN):           # Friction force based on Anderson et al. model [Viscous friction not included]
    ff = fN*(mu_d + (mu_s - mu_d)*np.exp(-(abs(v)/v_s)**p))*np.tanh(k_t*v)
    return ff

#%%% Friction_B      
def Friction_B(mu_s, mu_d, mu_v, v_t, fnt, v, fN):       # Friction force based on Brown-McPhee model [Viscous friction is included]
    vr = v/v_t
    ff = fN*(mu_d*np.tanh(4*vr) + (mu_s - mu_d)*vr/(0.25*vr**2 + 0.75)**2) + mu_v*v*np.tanh(4*fN/fnt)
    return ff

#%%% SDA_ptp
def SDA_ptp(Fi):                                         # Point-to-point spring-damper-actuator
    global Bodies, delta_ptp
    
    Pi     = Forces[Fi,0].iPindex    
    Pj     = Forces[Fi,0].jPindex 
    Bi     = Forces[Fi,0].iBindex  
    Bj     = Forces[Fi,0].jBindex 
    d      = Points[Pi,0].rP - Points[Pj,0].rP
    d_dot  = Points[Pi,0].rP_d - Points[Pj,0].rP_d
    L     = np.sqrt(d.T @ d)
    L_dot = (d.T @ d_dot)/L
    delta_ptp    = L - Forces[Fi,0].L0
    u      = d/L

    f = Forces[Fi,0].k*delta_ptp + Forces[Fi,0].dc*L_dot + Forces[Fi,0].f_a
    fi = f*u
    if Bi != 0:
        global Bodies
        Bodies[Bi,0].f = Bodies[Bi,0].f - fi
        Bodies[Bi,0].n = Bodies[Bi,0].n - Points[Pi,0].sP_r.T @ fi
    if Bj != 0:
        Bodies[Bj,0].f = Bodies[Bj,0].f + fi
        Bodies[Bj,0].n = Bodies[Bj,0].n + Points[Pj,0].sP_r.T @ fi
        
#%%% SDA_rot
def SDA_rot(Fi): #Rotational spring-damper-actuator
    global Bodies
    
    Bi = Forces[Fi,0].iBindex 
    Bj = Forces[Fi,0].jBindex 
    
    if Bi == 0:
        theta   = -Bodies[Bj,0].p
        theta_d = -Bodies[Bj,0].p_d
        T = Forces[Fi,0].k*(theta - Forces[Fi,0].theta0) + Forces[Fi,0].dc*theta_d + Forces[Fi,0].T_a
        Bodies[Bj,0].n = Bodies[Bj,0].n + T
    elif Bj == 0: 
        theta   = Bodies[Bi,0].p
        theta_d = Bodies[Bi,0].p_d 
        T = Forces[Fi,0].k*(theta - Forces[Fi,0].theta0) + Forces[Fi,0].dc*theta_d + Forces[Fi,0].T_a
        Bodies[Bi,0].n = Bodies[Bi,0].n - T
    else:
        theta   = Bodies[Bi,0].p - Bodies[Bj,0].p
        theta_d = Bodies[Bi,0].p_d - Bodies[Bj,0].p_d 
        T = Forces[Fi,0].k*(theta - Forces[Fi,0].theta0) + Forces[Fi,0].dc*theta_d + Forces[Fi,0].T_a
        Bodies[Bi,0].n = Bodies[Bi,0].n - T
        Bodies[Bj,0].n = Bodies[Bj,0].n + T

#%%% Force_array
def Force_array(t):
    # initialise body force vectors
    for Bi in range(1, nB): 
        Bodies[Bi,0].f = np.array([[0],[0]])
        Bodies[Bi,0].n = 0
        
    for Fi in range(1, nF):
        # class method/Dispatch method - "actual" switch 
        # define switch 
        class switch(object):
            def force_type(self, argument):                            # Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
                return method()                                        # Call the method as we return it
        
            # define "cases" 
            def weight(self):
                for Bi in range(1, nB): 
                    global Bodies
                    Bodies[Bi,0].f = Bodies[Bi,0].f + Bodies[Bi,0].wgt
                    
            def ptp(self):
                SDA_ptp(Fi)
                
            def rot_sda(self): 
                SDA_rot(Fi)
                
            def flocal(self):
                Bi = Forces[Fi,0].iBindex 
                global Bodies
                Bodies[Bi,0].f = Bodies[Bi,0].f + Bodies[Bi,0].A @ Forces[Fi,0].flocal
                
            def f(self):
                Bi = Forces[Fi,0].iBindex
                global Bodies
                Bodies[Bi,0].f = Bodies[Bi,0].f + Forces[Fi,0].f
                
            def trq(self):
                Bi = Forces[Fi,0].iBindex
                global Bodies
                Bodies[Bi,0].f = Bodies[Bi,0].n + Forces[Fi,0].T
                
            def user(self):
                if selection == 'a':
                    user_force_AA()
                elif selection == 'b':
                    user_force_Cart_C()
                elif selection =='c':
                    user_force_Cart_D()
                # elif selection == 'd':
                #     user_force_CB()
                elif selection == 'd':
                    user_force_MP_A() 
                # elif selection == 'f':
                #     user_force_Rod()                    
                else:
                    print('Undefined User Force')
         
        switch().force_type(Forces[Fi,0].type) # implement switch
        
    g = np.zeros((nB3,1))
    
    for Bi in range(1, nB): 
        
        ks = Bodies[Bi,0].irc
        ke = ks + 3
        g[ks:ke,0] = np.concatenate( (Bodies[Bi,0].f, Bodies[Bi,0].n), axis=None)
    return g





################################################################
#
# Functions
#
################################################################
#WARNING WARNING WARNING WARNING two funct_c No function overloading in python
#WARNING WARNING WARNING WARNING
#WARNING WARNING WARNING WARNING
#WARNING WARNING WARNING WARNING
#WARNING WARNING WARNING WARNING
#%%% funct_a
def funct_a(Ci, x): # Funciton type 'a'
    c    = Functs[Ci,0].coeff
    f    = c[1,0] + c[2,0]*x + c[3,0]*(x**2)
    f_d  = c[2,0] + c[4,0]*x
    f_dd = c[4]
    return f, f_d, f_dd

#%%% funct_b
def funct_b(Ci, xx): #Function type 'b'
    c = Functs[Ci,0].coeff
    
    if xx <= Functs[Ci,0].t_start:
        f    = Functs[Ci,0].f_start
        f_d  = 0
        f_dd = 0
    elif xx > Functs(Ci).t_start and xx < Functs(Ci).t_end:
        x    = xx - Functs[Ci,0].t_start
        f    = c[1,0]*x**3 + c[2,0]*x**4 + c[3,0]*x**5 + Functs[Ci,0].f_start
        f_d  = c[4,0]*x**2 + c[5,0]*x**3 + c[6,0]*x**4
        f_dd = c[7,0]*x   + c[8,0]*x**2 + c[9,0]*x**3
    else:
        f    = Functs[Ci,0].f_end;
        f_d  = 0
        f_dd = 0
        
    return f, f_d, f_dd

#%%% funct_c
def funct_c(Ci, xx): #Function type 'c'
    c = Functs[Ci,0].coeff
        
    if xx <= Functs[Ci,0].t_start:
        f    = Functs[Ci,0].f_start
        f_d  = 0
        f_dd = 0
    elif xx > Functs[Ci,0].t_start and xx < Functs[Ci,0].t_end:
        x    = xx - Functs[Ci,0].t_start
        f    = c[1,0]*x**4 + c[2,0]*x**5 + c[3,0]*x**6 + Functs[Ci,0].f_start
        f_d  = c[4,0]*x**3 + c[5,0]*x**4 + c[6,0]*x**5
        f_dd = c[7,0]*x**2 + c[8,0]*x**3 + c[9,0]*x**4
    else:
        f    = 0 # this should be undefined
        f_d  = Functs[Ci,0].dfdt_end
        f_dd = 0
        
    return f, f_d, f_dd

#WARNING WARNING WARNING python does not support overloaded functions
#%%% funct_ccc
def funct_c(Ci, xx):                #Function type 'c' 
    c = Functs[Ci,0].coeff
    
    if xx <= Functs[Ci,0].t_start:
        f    = Functs[Ci,0].f_start
        f_d  = 0
        f_dd = 0
    elif xx > Functs[Ci,0].x_start and xx < Functs[Ci,0].x_end:
        x = xx - Functs[Ci,0].x_start
        f    = c[1,0]*x**3 + c[2,0]*x**4  + c[3,0]*x**5  + c[4,0]*x**6  + c[5,0]*x**7  + Functs[Ci,0].f_start
        f_d  = c[6,0]*x**2 + c[7,0]*x**3  + c[8,0]*x**4  + c[9,0]*x**5  + c[10,0]*x**6
        f_dd = c[11,0]*x   + c[12,0]*x**2 + c[13,0]*x**3 + c[14,0]*x**4 + c[15,0]*x**5
    else:
        f    = Functs[Ci,0].f_end
        f_d  = 0
        f_dd = 0 
        
    return f, f_d, f_dd

#%%% functs
def functs(Ci, t):
    # define switch 
    class switch(object):
        def Functs_type(self, argument):                            # Dispatch method
            method_name = argument
            method = getattr(self, method_name, lambda: "Invalid")  # Get the method from 'self'. Default to a lambda.
            return method()                                         # Call the method as we return it

        # define "cases" 
        def a(self):
            global _f_
            _f_ =  funct_a(Ci,t)
            
        def b(self):
            global _f_
            _f_ =  funct_b(Ci,t)
        
        def c(self):
            global _f_
            _f_ =  funct_c(Ci,t)
        
        def d(self):
            global _f_
            _f_ =  funct_d(Ci,t)
     
    switch().Functs_type(Functs[Ci,0].type) # implement switch
    return _f_
    
#%%% functData 
def functionData(Ci):
    # define switch 
    class switch(object):
        def Functs_type(self, argument):                           # Dispatch method
            method_name = argument
            method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
            return method()                                        # Call the method as we return it

        # define "cases" 
        def a(self):
            global Functs
            Functs[Ci,0].ncoeff = 4
            Functs[Ci,0].coeff[4-1,0] = 2*Functs[Ci,0].coeff[3-1,0]

        def b(self):
            global Functs
            Functs[Ci,0].ncoeff = 9
            xe = Functs[Ci,0].t_end - Functs[Ci,0].t_start
            fe = Functs[Ci,0].f_end - Functs[Ci,0].f_start
            C = np.array([  [xe**3,     xe**4,      xe**5],
                            [3*xe**2,   4*xe**3,    5*xe**4],
                            [6*xe,      12*xe**2,   20*xe**3] ])
            sol = np.linalg.solve( C, np.array([ [fe], [0], [0] ]) )
            
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, sol), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [3*sol[1,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [4*sol[2,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [5*sol[3,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [6*sol[1,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [12*sol[2,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [20*sol[3,0]] ])), axis=0 )

        def c(self):
            global Functs
            Functs[Ci,0].ncoeff = 9
            xe                  = Functs[Ci,0].t_end - Functs[Ci,0].t_start
            fpe                 = Functs[Ci,0].dfdt_end
            C                   = np.array([ [4*xe**3,   5*xe**4,    6*xe**5],
                                             [12*xe**2,  20*xe**3,   30*xe**4],
                                             [24*xe,     60*xe**2,   120*xe**3] ])
            sol = np.linalg.solve( C, np.array([ [fpe], [0], [0] ]) )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, sol), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [4*sol[1,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [5*sol[2,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [6*sol[3,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [12*sol[1,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [20*sol[2,0]] ])), axis=0 )
            Functs[Ci,0].coeff = np.concatenate( (Functs[Ci,0].coeff, np.array([ [30*sol[3,0]] ])), axis=0 )       
     
    switch().Functs_type(Functs[Ci,0].type) # implement switch




################################################################
#
# helper functions
#
################################################################
#%% Matrix A 
def Matrix_A(p): # This function computes the rotational transformation matrix A
    c = np.cos(p)
    s = np.sin(p)
    A = np.array([ [c, -s],
                   [s, c] ])
    return A

#%% s_rot 
def s_rot(s): # This function rotates an array 90degrees positively 
    s_r = np.array([ [-s[1,0]], [s[0,0]] ])
    return s_r 




################################################################
#
# initialise
#
################################################################
#import numpy as np


def initialize():
    import numpy as np
##### include global variables
    global Bodies, nB, nB3, nB6      
    global Points, nP, Points_anim, nPanim, nPtot
    global Uvectors, nU 
    global Joints, nJ, nConst
    global Forces, nF
    global M_array, M_inv_array
    global Functs, nFc
    global ZZ, redund, cfriction
    global num, D, Dt, Lambda 
    global xmin, xmax, ymin, ymax
    global showtime, t10
    global flags, pen_d0
    
    bodycolor = ['r', 'g' ,'b', 'c', 'm']
    
    num = 0 # number of function evaluations
    t10 = 0
    flags = np.zeros( (10,1) )
    pen_d0 = np.zeros( (10,1) )
    
#%%% Bodies 
    nB  = len(Bodies)
    nB3 = 3*(nB)
    nB6 = 6*(nB)
    
    for Bi in range(1, nB): 
        Bodies[Bi,0].irc    = 3*(Bi-1) + 1
        Bodies[Bi,0].irv    = 3*(nB-1) + 3*(Bi-1) + 1
        Bodies[Bi,0].m_inv  = 1/Bodies[Bi,0].m
        Bodies[Bi,0].J_inv  = 1/Bodies[Bi,0].J
        Bodies[Bi,0].A      = Matrix_A(Bodies[Bi,0].p)
        Bodies[Bi,0].color  = bodycolor[Bi]

#%%% Mass (inertia) matrix as an array 
    M_array     = np.zeros((nB3,1))
    M_inv_array = np.zeros((nB3,1))
    
    for Bi in range(1, nB): 
        is_                   = 3*(Bi - 1) + 1
        ie                    = is_ + 2 + 1 
        M_array[is_:ie,0]     = [Bodies[Bi,0].m, Bodies[Bi,0].m, Bodies[Bi,0].J ]
        M_inv_array[is_:ie,0] = [Bodies[Bi,0].m_inv, Bodies[Bi,0].m_inv, Bodies[Bi,0].J_inv]
        
#%%% Points 
    nP      = len(Points)
    nPanim  = len(Points_anim)
    #nPtot   = nP + nPanim - 1
    nPtot = nP 
    Points  = np.concatenate( (Points, Points_anim),axis=0 ) 
    
    print("==================================")
    print("nPtot",nPtot)
    for Pi in range(1,nPtot): 
        print("Pi",Pi)
        if Points[Pi,0].Bindex == 0:
            Points[Pi,0].sP     = Points[Pi,0].sPlocal
            Points[Pi,0].sP_r   = s_rot(Points[Pi,0].sP)
            Points[Pi,0].rP     = Points[Pi,0].sP
        
        print(Points[Pi,0].Bindex)
        print("nB",nB)
        for Bi in range(1,nB): 
            if int(Points[Pi,0].Bindex) == int(Bi):
                length           = len(Bodies[Bi,0].pts) #current length of pts
                Bodies[Bi,0].pts = np.concatenate( (Bodies[Bi,0].pts,np.array([ [Pi] ]) ), axis=0 )
                
                print(Bodies[Bi,0].pts)
                
    print("==================================")
    
#%%% Unit vectors 
    nU = len(Uvectors)
    
    for Vi in range(1,nU): 
        if Uvectors.size == 0:
            pass
        elif Uvectors[Vi,0].Bindex == 0:
            Uvectors[Vi,0].u   = Uvectors[Vi,0].ulocal
            Uvectors[Vi,0].u_r = s_rot(Uvectors[Vi,0].u)
            
#%%% Force elements 
    nF = len(Forces)
    
    for Fi in range(1,nF): 
        # define switch 
        class switch(object):
            def force_type(self, argument):                            # Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
                return method()                                        # Call the method as we return it
        
            # define "cases" 
            def weight(self):
                ug = Forces[Fi,0].gravity*Forces[Fi,0].wgt
                for Bi in range(1,nB):
                    Bodies[Bi,0].wgt = Bodies[Bi,0].m*ug
                    
            def ptp(self):
                Pi = Forces[Fi,0].iPindex  
                Pj = Forces[Fi,0].jPindex 
                Forces[Fi,0].iBindex = Points[Pi,0].Bindex
                Forces[Fi,0].jBindex = Points[Pj,0].Bindex              
            
        switch().force_type(Forces[Fi,0].type)  # implement switch      

#%%% Joints 
    nJ = len(Joints)
    cfriction = 0
    
    # Assign number of constraints and number of bodies to each joint type  
    for Ji in range(1,nJ): 
        # define switch 
        class switch(object):
            def joint_type(self, argument):                                                # Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: print("Undefined joint type")) # Get the method from 'self'. Default to a lambda.
                return method()                                                            # Call the method as we return it
        
            # define "cases" 
            def rev(self):
                Joints[Ji,0].mrows = 2 
                Joints[Ji,0].nbody = 2
                Pi = Joints[Ji,0].iPindex 
                Pj = Joints[Ji,0].jPindex
                Bi = Points[Pi,0].Bindex
                Joints[Ji,0].iBindex = Bi
                Bj = Points[Pj,0].Bindex
                Joints[Ji,0].jBindex = Bj
                
                if Joints[Ji,0].fix == 1:
                    Joints[Ji,0].mrows = 3
                    if Bi == 0:
                        Joints[Ji,0].p0 = - Bodies[Bj,0].p
                    elif Bj == 0:
                        Joints[Ji,0].p0 = Bodies[Bi,0].p
                    else:
                        Joints[Ji,0].p0 = Bodies[Bi,0].p - Bodies[Bj,0].p
                        
            def tran(self):
                Joints[Ji,0].mrows = 2;
                Joints[Ji,0].nbody = 2
                Pi = Joints[Ji,0].iPindex
                Pj = Joints[Ji,0].jPindex
                Bi = Points[Pi,0].Bindex
                Joints[Ji,0].iBindex = Bi
                Bj = Points[Pj,0].Bindex
                Joints[Ji,0].jBindex = Bj
                if Joints[Ji,0].fix == 1:
                    Joints[Ji,0].mrows = 3
                    if Bi == 0:
                        Joints[Ji,0].p0 = np.linalg.norm(Points[Pi,0].rP - Bodies[Bj,0].r - 
                                                         Bodies[Bj,0].A@Points[Pj,0].sPlocal)
                    elif Bj == 0:
                        Joints[Ji,0].p0 = np.linalg.norm(Bodies[Bi,0].r + Bodies[Bi,0].A@Points[Pi,0].sPlocal - 
                                                         Points[Pj,0].rP)
                    else:
                        Joints[Ji,0].p0 = np.linalg.norm(Bodies[Bi,0].r + Bodies[Bi,0].A@Points[Pi,0].sPlocal - 
                                                         Bodies[Bj,0].r - Bodies[Bj,0].A@Points[Pj,0].sPlocal)
                            
            def rev_rev(self): 
                Joints[Ji,0].mrows = 1 
                Joints[Ji,0].nbody = 2
                Pi = Joints[Ji,0].iPindex; Pj = Joints[Ji,0].jPindex
                Joints[Ji,0].iBindex = Points[Pi,0].Bindex
                Joints[Ji,0].jBindex = Points[Pj,0].Bindex

            def rev_tran(self): 
                Joints[Ji,0].mrows = 1
                Joints[Ji,0].nbody = 2
                Pi = Joints[Ji,0].iPindex
                Pj = Joints[Ji,0].jPindex
                Joints[Ji,0].iBindex = Points[Pi,0].Bindex
                Joints[Ji,0].jBindex = Points[Pj,0].Bindex

            def rel_rot(self): 
                Joints[Ji,0].mrows = 1
                Joints[Ji,0].nbody = 1

            def rel_tran(self): 
                Joints[Ji,0].mrows = 1
                Joints[Ji,0].nbody = 1  

            def disc(self):
                Joints[Ji,0].mrows = 2 
                Joints[Ji,0].nbody = 1

            def rigid(self):                                            
                Joints[Ji,0].mrows = 3; 
                Joints[Ji,0].nbody = 2;
                Bi = Joints[Ji,0].iBindex   
                Bj = Joints[Ji,0].jBindex
                if Bi == 0:
                    Joints[Ji,0].d0 = -Bodies[Bj,0].A.T@Bodies[Bj,0].r
                    Joints[Ji,0].p0 = -Bodies[Bj,0].p
                elif Bj == 0:
                    Joints[Ji,0].d0 = Bodies[Bi,0].r
                    Joints[Ji,0].p0 = Bodies[Bi,0].p
                else:
                    Joints[Ji,0].d0 = Bodies[Bj,0].A.T@(Bodies[Bi,0].r - Bodies[Bj,0].r)
                    Joints[Ji,0].p0 = Bodies[Bi,0].p - Bodies[Bj,0].p
                    
        switch().joint_type(Joints[Ji,0].type) # implement switch     
        
        
                    
#%%% Functions 
    nFc = len(Functs)
    if Functs.size == 0:
        pass
    else:
        for Ci in range(1,nFc):
            functionData(Ci)
        
#%%% Constraints & row/col. pointers 
# Compute number of constraints and determine row/column pointer
    nConst = 0

    for Ji in range(1,nJ): 
        Joints[Ji,0].rows = nConst + 1
        Joints[Ji,0].rowe = nConst + Joints[Ji,0].mrows
        nConst = Joints[Ji,0].rowe
        Bi = Joints[Ji,0].iBindex
        if Bi != 0:
            Joints[Ji,0].colis = 3*(Bi - 1) + 1
            Joints[Ji,0].colie = 3*Bi

        Bj = Joints[Ji,0].jBindex
        if Bj != 0:
            Joints[Ji,0].coljs = 3*(Bj - 1) + 1
            Joints[Ji,0].colje = 3*Bj
            



################################################################
#
# Jacobian
#
################################################################
 
def Jacobian(t):
    global  nJ, nConst, nB3, D #rs, re, cis, cie, cjs, cje
    
    D = np.zeros((nConst,nB3))
    
    for Ji in range(1,nJ):
        if Joints[Ji,0].type == 'rev':
            Di, Dj = J_rev(Ji)
        elif Joints[Ji,0].type == 'tran':
            Di, Dj = J_tran(Ji)
        elif Joints[Ji,0].type == 'disc':
            Di = J_disc(Ji)
        elif Joints[Ji,0].type == 'rev_rev':
            Di, Dj = J_rev_rev(Ji)       
        elif Joints[Ji,0].type == 'rev_tran':
            Di, Dj = J_rev_tran(Ji)
        elif Joints[Ji,0].type == 'rel_rot':
            Di, Dj = J_rel_rot(Ji)   
        elif Joints[Ji,0].type == 'rel_tran':
            Di, Dj = J_rel_tran(Ji)
        elif Joints[Ji,0].type == 'rigid':
            Di, Dj = J_rigid(Ji)               
    
        rs  = Joints[Ji,0].rows -1  
        re  = Joints[Ji,0].rowe
    
        if Joints[Ji,0].iBindex != 0:
            cis = Joints[Ji,0].colis -1 
            cie = Joints[Ji,0].colie
            D[rs:re,cis:cie] = Di

        if Joints[Ji,0].jBindex != 0:
            cjs = Joints[Ji,0].coljs -1 
            cje = Joints[Ji,0].colje
            D[rs:re,cjs:cje] = Dj
        
    return D



################################################################
#
# JOINTS
#
################################################################
 
def A_disc(Ji):
    f = np.array([[0],
              [0]])
    return f

def C_disc(Ji):
    Bi = Joints[Ji,0].iBindex
    f = np.array([ [Bodies[Bi,0].r[2,0] - Joints[Ji,0].R], 
                    [Bodies[Bi,0].r[1,0] - Joints[Ji,0].x0 + Joints[Ji,0].R*(Bodies[Bi,0].p - Joints[Ji,0].p0)] ])
    return f

def J_disc(Ji):
    Di = np.array([ [0, 1, 0],
               [1, 0, Joints[Ji,0].R] ])
    return Di

#%%%% rel-rot
def A_rel_rot(Ji,t):
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    f = fun_dd
    return f

def C_rel_rot(Ji):
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    Bi = Joints[Ji,0].iBindex
    Bj = Joints[Ji,0].jBindex
    
    if (Bi == 0):
        f = -Bodies[Bj,0].p - fun
    elif (Bj == 0):
        f =  Bodies[Bi,0].p - fun
    else:
        f =  Bodies[Bi,0].p - Bodies[Bj,0].p - fun
        
    return f

def J_rel_rot(Ji):
    global Di, Dj
    Di = np.array([ [0, 0,  1] ])
    Dj = np.array([ [0, 0, -1] ])
    
    return Di, Dj

def V_rel_rot(Ji):
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    f = fun_d
    return f

#%%%% rel-tran  
def A_rel_tran(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    Bi = Joints[Ji,0].iBindex
    Bj = Joints[Ji,0].jBindex
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    d_d  = Points[Pi,0].rP_d - Points[Pj,0].rP_d
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    
    f = fun*fun_dd + fun_d**2
    
    if (Bi == 0):
        f = f + d.T*s_rot(Points[Pj,0].sP_d).T*Bodies[Bj,0].p_d
    elif (Bj == 0):
        f = f - d.T*s_rot(Points[Pi,0].sP_d).T*Bodies[Bi,0].p_d - d_d.T*d_d
    else:
        f = f + d.T*s_rot(Points[Pj,0].sP_d).T*Bodies[Bj,0].p_d - d.T*s_rot(Points[Pi,0].sP_d).T*Bodies(Bi).p_d - d_d.T*d_d

    return f

def C_rel_tran(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    
    f = (d.T*d - fun**2)/2

    return f

def J_rel_tran(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    
    Di = np.array([ [ d.T,  d.T*Points[Pi,0].sP_r] ]).T
    Dj = np.array([ [-d.T, -d.T*Points[Pj,0].sP_r] ]).T
    
    return Di, Dj

def V_rel_tran(Ji):
    fun, fun_d, fun_dd = functs(Joints[Ji,0].iFunct, t)
    f = fun*fun_d
    
    return f

#%%%% rev
def A_rev(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    Bi = Points[Pi,0].Bindex
    Bj = Points[Pj,0].Bindex

    if Bi == 0:
        f = s_rot(Points[Pj,0].sP_d)*Bodies[Bj,0].p_d

    elif Bj == 0:
        f = -s_rot(Points[Pi,0].sP_d)* Bodies[Bi,0].p_d
        
    else:
        f = -s_rot(Points[Pi,0].sP_d) * Bodies[Bi,0].p_d + s_rot(Points[Pj,0].sP_d)* Bodies[Bj,0].p_d

    if Joints[Ji,0].fix == 1:
        f = np.array([ [f], 
                       [0] ])
        
    return f

def C_rev(Ji):
    Pi = Joints[Ji,0].iPindex 
    Pj = Joints[Ji,0].jPindex 

    f = Points[Pi,0].rP - Points[Pj,0].rP
    if Joints[Ji,0].fix == 1:
        Bi = Joints[Ji,0].iBindex
        Bj = Joints[Ji,0].jBindex
        
        if Bi == 0:
            f = np.array([ [f], [(- Bodies[Bj,0]).p - Joints[Ji,0].p0] ])
        elif Bj == 0:
            f = np.array([ [f],[Bodies[Bi,0].p - Joints[Ji,0].p0] ])
        else:
            f = np.array([ [f],[Bodies[Bi,0].p - Bodies[Bj,0].p - Joints[Ji,0].p0] ])
            
    return f

def J_rev(Ji):
    Pi = Joints[Ji,0].iPindex   
    Pj = Joints[Ji,0].jPindex 
    
    Di = np.concatenate(( np.eye(2),  Points[Pi,0].sP_r),axis=1 )
    Dj = np.concatenate( (-np.eye(2), -Points[Pj,0].sP_r), axis=1) 
    
    if Joints[Ji,0].fix == 1:
        Di = np.array([ [Di], [0,0,1] ])
        Dj = np.array([ [Dj], [0,0,-1] ])
        
    return Di, Dj

#%%%% rev-rev
def A_rev_rev(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    Bi = Joints[Ji,0].iBindex
    Bj = Joints[Ji,0].jBindex
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    d_d  = Points[Pi,0].rP_d - Points[Pj,0].rP_d

    L = Joints[Ji,0].L
    u = d/L
    u_d = d_d/L
    
    f = - u_d.T @ d_d
    
    if (Bi == 0):
        f = f + u.T@s_rot(Points[Pj,0].sP_d)*Bodies[Bj,0].p_d
    elif (Bj == 0):
        f = f - u.T@s_rot(Points[Pi,0].sP_d)*Bodies[Bi,0].p_d
    else:
        f = f - u.T@(s_rot(Points[Pi,0].sP_d*Bodies[Bi,0].p_d - Points[Pj,0].sP_d*Bodies[Bj,0].p_d))

    return f

def C_rev_rev(Ji):
    Pi = Joints(Ji).iPindex
    Pj = Joints(Ji).jPindex
    d = Points(Pi).rP - Points(Pj).rP
    L = Joints(Ji).L
    u = d/L
    f = (u.T@d - L)/2
    return f

def J_rev_rev(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    L = Joints[Ji,0].L
    u = d/L
    
    Di = np.array([[ u.T,  u.T*Points[Pi,0].sP_r]])
    Dj = np.array([[-u.T, -u.T*Points[Pj,0].sP_r]])

    return Di, Dj

#%%%% rev-tran
def A_rev_tran(Ji):
    Pi = Joints[Ji,0].iPindex
    Pj = Joints[Ji,0].jPindex
    Bi = Joints[Ji,0].iBindex
    Bj = Joints[Ji,0].jBindex;
    ui  = Uvectors(Joints[Ji,0].iUindex).u
    ui_d = Uvectors(Joints[Ji,0].iUindex).u_d
    d  = Points[Pi,0].rP - Points[Pj,0].rP
    d_d  = Points[Pi,0].rP_d - Points[Pj,0].rP_d
    
    if Bi == 0:
        f = ui.T*Points[Pj,0].sP_d*Bodies[Bj,0].p_d
    elif Bj == 0:
        f = ui_d.T@(d*Bodies[Bi,0].p_d + 2*s_rot(d_d)) - ui.T@Points[Pi,0].sP_d*Bodies[Bi,0].p_d
    else:
        f = ui_d.T@(d*Bodies[Bi,0].p_d + 2*s_rot(d_d)) - ui.T@(Points[Pi,0].sP_d*Bodies[Bi,0].p_d - Points[Pj,0].sP_d*Bodies[Bj,0].p_d)
   
    return f

def C_rev_tran(Ji):
    Pi   = Joints[Ji,0].iPindex
    Pj   = Joints[Ji,0].jPindex
    ui_r = Uvectors(Joints[Ji,0].iUindex).u_r
    d    = Points[Pi,0].rP - Points[Pj,0].rP
    f    = ui_r.T@d - Joints[Ji,0].L
    
    return f

def J_rev_tran(Ji):
    Pi   = Joints[Ji,0].iPindex
    Pj   = Joints[Ji,0].jPindex
    ui   = Uvectors(Joints[Ji,0].iUindex).u;
    ui_r  = Uvectors(Joints[Ji,0].iUindex).u_r
    d    = Points[Pi,0].rP - Points[Pj,0].rP
    Di   = np.array([[ ui_r.T,  ui.T*(Points[Pi,0].sP - d)]])
    Dj   = np.array([[-ui_r.T, -ui.T*Points[Pj,0].sP]])
    
    return Di, Dj

#%%%% rigid
def A_rigid(Ji):
    Bj = Joints[Ji,0].jBindex
    f  = np.array([[0, 0, 0]]).T
    if Bj != 0:
        f = np.array([ [-Bodies[Bj,0].A@Joints[Ji,0].d0*Bodies[Bj,0].p_d**2, 0] ]).T

    return f

def C_rigid(Ji):
    Bi = Joints[Ji,0].iBindex
    Bj = Joints[Ji,0].jBindex
    
    if Bi == 0:
        f = np.array([ [ -1*(Bodies[Bj,0].r + Bodies[Bj,0].A@Joints[Ji,0].d0),
                               -Bodies[Bj,0].p - Joints[Ji,0].p0] ]).T
    elif Bj == 0:
        f = np.array([ [Bodies[Bi,0].r - Joints[Ji,0].d0,
                     Bodies[Bi,0].p - Joints[Ji,0].p0] ]).T
    else:
        f = np.array([ [Bodies[Bi,0].r - (Bodies[Bj,0].r + Bodies[Bj,0].A@Joints[Ji,0].d0),
                       Bodies[Bi,0].p - Bodies[Bj,0].p - Joints[Ji,0].p0] ]).T
    
    return f

def J_rigid(Ji):
    Bj = Joints[Ji,0].jBindex
    Di = np.eye[3]
    
    if Bj != 0:
        Dj = np.array([ [-np.eye[2], -s_rot(Bodies[Bj,0].A@Joints[Ji,0].d0)],
               [0,  0,   -1] ])
    
    return Di, Dj

#%%%% tran
def A_tran(Ji):
    Bi    = Joints[Ji,0].iBindex 
    Bj    = Joints[Ji,0].jBindex 
    Pi    = Joints[Ji,0].iPindex 
    Pj    = Joints[Ji,0].jPindex 
    ujd   = Uvectors[Joints[Ji,0].jUindex,0].u_d
    ujd_r = s_rot(ujd)
        
    if Bi == 0:
        f2 = 0
    elif Bj == 0:
        f2 = 0
    else:
        f2 = ujd.T@(Bodies[Bi,0].r - Bodies[Bj,0].r)*Bodies[Bi,0].p_d - 2*ujd_r.T@(Bodies[Bi,0].r_d - Bodies[Bj,0].r_d)
      
    f  = np.atleast_2d( np.concatenate( (f2, np.array([[0]]) ), axis=None) ).T
 
    if Joints[Ji,0].fix == 1:
        d    = Points[Pi,0].rP - Points[Pj,0].rP
        d_d  = Points[Pi,0].rP_d - Points[Pj,0].rP_d
        L    = Joints[Ji,0].p0; u = d/L; u_d = d_d/L
        f3   = (- u_d.T@d_d)
        
        if Bi == 0:
            f3 = (- u_d.T@d_d) + u.T@s_rot(Points[Pj,0].sP_d)@Bodies[Bj,0].p_d
        elif Bj == 0:
            f3 = (- u_d.T@d_d) - u.T@s_rot(Points[Pi,0].sP_d)@Bodies[Bi,0].p_d
        else:
            f3 = (- u_d.T@d_d) - u.T@(s_rot(Points[Pi,0].sP_d*Bodies[Bi,0].p_d -
                                 Points[Pj,0].sP_d*Bodies[Bj,0].p_d))

        f = np.array([[f], [f3]])
        
    return f

def C_tran(Ji):
    Pi   = Joints[Ji,0].iPindex 
    Pj   = Joints[Ji,0].jPindex 
    uj_r = Uvectors(Joints[Ji,0].jUindex).u_r
    ui   = Uvectors(Joints[Ji,0].iUindex).u
    d    = Points[Pi,0].rP - Points[Pj,0].rP
    f    = np.array([ [uj_r.T@d], [uj_r.T@ui] ]).T
    
    if Joints[Ji,0].fix == 1:
        f = np.array([ [f],
                  [(ui.T@d - Joints[Ji,0].p0)/2] ])
        
    return f

def J_tran(Ji):
    Pi   = Joints[Ji,0].iPindex 
    Pj   = Joints[Ji,0].jPindex 
    uj   = Uvectors[Joints[Ji,0].jUindex,0].u
    uj_r = Uvectors[Joints[Ji,0].jUindex,0].u_r
    d    = Points[Pi,0].rP - Points[Pj,0].rP
    Di1  = np.concatenate( (uj_r.T, uj.T@Points[Pi,0].sP), axis=1 )
    Di2  = np.array([[0,0,1]])
    Di   = np.concatenate((Di1, Di2), axis=0)
    Dj1  = np.concatenate( (-uj_r.T, -uj.T@(Points[Pi,0].sP + d)), axis=1 )
    Dj2  = np.array([[0,0,-1]])
    Dj   = np.concatenate((Dj1, Dj2), axis=0)
        
    return Di, Dj



################################################################
#
# RHS
#
################################################################
 
def RHSAcc(t):
    global nConst, nJ
    
    rhs = np.zeros((nConst,1))
    
    for Ji in range(1,nJ):
        if Joints[Ji,0].type == 'rev':
            f = A_rev(Ji)
             
        if Joints[Ji,0].type == 'tran':
            f = A_tran(Ji)
            
        if Joints[Ji,0].type == 'rev_rev':
            f = A_rev_rev(Ji)
            
        if Joints[Ji,0].type == 'rev_tran':
            f = A_rev_tran(Ji)
            
        if Joints[Ji,0].type == 'rigid':
            f = A_rigid(Ji)
            
        if Joints[Ji,0].type == 'disc':
            f = A_disc(Ji)
            
        if Joints[Ji,0].type == 'rel_rot':  
            f = A_rel_rot(Ji,t)
            
        if Joints[Ji,0].type == 'rel_tran':
            f = A_rel_tran(Ji)

        rs = Joints[Ji,0].rows -1
        re = Joints[Ji,0].rowe 
        rhs[rs:re] = f
        
    return rhs

#%%% RHSVel
import numpy as np
def RHSVel(t):
    global nConst, nJ
    
    rhs = np.zeros((nConst,1))
    
    for Ji in range(1,nJ):
        if Joints[Ji,0].type == 'rel-rot':
            V_rel_rot()
            rhs[Joints[Ji,0].rows-1:Joints[Ji,0].rowe] = f
        if Joints[Ji,0].type == 'rel-tran':
            V_rel_tran()
            rhs[Joints[Ji,0].rows-1:Joints[Ji,0].rowe] = f
        
    return None        



#################################################################
##
## Structures
##
#################################################################
#import numpy as np 
##%%% Body Structure
#class Body_struct:
    #def __init__(self):
        
        #self.m      = 1                      # mass
        #self.J      = 1                      # moment of inertia
        #self.r      = np.array([[0,0]]).T 	 # x, y coordinates
        #self.p      = 0                      # angle phi
        #self.r_d    = np.array([[0,0]]).T    # time derivative of x and y
        #self.p_d    = 0                      # time derivative of phi
        #self.A      = np.eye(2)              # rotational transformation matrix
        #self.r_dd   = np.array([[0,0]]).T    # x_double_dot,y_double_dot
        #self.p_dd   = 0                      # 2nd time derivative of phi  #  index of the 1st element of r in u or u_dot
        #self.irc    = 0                      # index of 1st element of r in u or u_dot
        #self.irv    = 0                      # index of the 1st element of r_dot in u or u_dot
        #self.ira    = 0                      # index of the 1st element of r_dot2 in v_dot

        #self.m_inv  = 1                         # mass inverse
        #self.J_inv  = 1                         # inverse of moment of inertia
        #self.wgt    = np.array([[0,0]]).T       # weight of body as a force vector
        #self.f      = np.array([[0,0]]).T       # sum of forces that act on the body
        #self.n      = 0                         # sum of moments that act on the body
        #self.shape  = ''                        # 'circle', 'rect', line
        #self.R      = 1                         # radius of the circle
        #self.circ   = np.array([[]]).T          # points on circumference of the circle
        #self.W      = 0                         # width of the rectangle
        #self.H      = 0                         # height of the rectangle
        #self.color  ='k'                        # default color for the body
        #self.P4     = np.array([[]]).T          # corners of the rectangle
        #self.pts    = np.array([[]]).T          # point indexes associated with this body
        #return


##%% Force Structure
#class Force_struct:
    #def __init__(self):
        #self.type       = 'ptp'                 # element type: ptp, rot_sda, weight, fp, f, T
        #self.iPindex    = 0                     # index of the head (arrow) point
        #self.jPindex    = 0                     # index of the tail point
        #self.iBindex    = 0                     # index of the head (arrow) body
        #self.jBindex    = 0                     # index of the tail body
        #self.k          = 0                     # spring stiffness
        #self.L0         = 0                     # undeformed length
        #self.theta0     = 0                     # undeformed angle
        #self.dc         = 0                     # damping coefficient
        #self.f_a        = 0                     # constant actuator force
        #self.T_a        = 0                     # constant actuator torque
        #self.gravity    = 9.81                  # gravitational constant
        #self.wgt        = np.array([[0,-1]]).T  # gravitational direction
        #self.flocal     = np.array([[0,0]]).T   # constant force in local frame
        #self.f          = np.array([[0,0]]).T   # constant force in x-y frame
        #self.t          = 0                     # constant torque in x-y frame
        #self.iFunct     = 0
        #return


##%%% Joint Structure
#class Joint_struct:
    #def __init__(self):
        #self.type       = 'rev'     # joint type: rev, tran, rev-rev, rev-tran, rigid, disc, rel-rot, rel-tran

        #self.iBindex    = 0         # body index i
        #self.jBindex    = 0         # body index j
        #self.iPindex    = 0         # point Pi index
        #self.jPindex    = 0         # point Pj index
        #self.iUindex    = 0         # unit vector u_i index
        #self.jUindex    = 0         # unit vector u_j index
        #self.iFunct     = 0         # analytical function index
        #self.L          = 0         # constant length

        #self.R      = 1                 # constant radius
        #self.x0     = 0                 # initial condition x for disc
        #self.p0     = 0                 # initial condition phi for a disc (or rigid)
        #self.d0     = np.array([[]]).T  # initial condition for d (rigid)
        #self.fix    = 0                 # fix relative dof if = 1 (rev or tran)
        #self.nboby  = 2                 # number of moving bodies involved
        #self.mrows  = 2                 # number of rows (constraints)

        #self.rows     = 0               # row index-start
        #self.rowe     = 0               # row index-end
        #self.colis    = 0               # column index for body i-start
        #self.colie    = 0               # column index for body i-end
        #self.coljs    = 0               # column index for body j-start
        #self.colje    = 0               # column index for body j-end
        #self.lagrange =np.zeros((3,1))  # Lagrange multipliers
        #return


##%%% Point Structure
#class Point_struct:
    #def __init__(self):
        #self.Bindex     = 0                     # body index
        #self.sPlocal    = np.array([[0,0]]).T   # body-fixed coordinates
        #self.sP         = np.array([[0,0]]).T   # x, y components of vector s
        #self.sP_r       = np.array([[0,0]]).T   # vector s rotated
        #self.rP         = np.array([[0,0]]).T   # x, y coordinates of the point
        #self.sP_d       = np.array([[0,0]]).T   # s_P_dot
        #self.rP_d       = np.array([[0,0]]).T   # r_P_dot
        #self.rP_dd      = np.array([[0,0]]).T   # r_P_dot2

        #return


##%%% Unit Structure
#class Unit_struct:
    #def __init__(self):
        #self.Bindex = 0                     # body index
        #self.ulocal = np.array([[1,0]]).T   # u_prime; xi and eta components
        #self.u      = np.array([[0,0]]).T   # x, y components
        #self.u_r    = np.array([[0,0]]).T   # vector u rotated
        #self.u_d    = np.array([[0,0]]).T   # u_dot
        #return

##%%% Function Structure
#class Funct_struct:
    #def __init__(self):
        #self.type='a'                    # function type a, b, or c
        #self.t_start=0                   # required for functions b, c
        #self.f_start=0                   # required for functions b, c
        #self.t_end=1                     # required for functions b, c
        #self.f_end=1                     # required for functions b
        #self.dfdt_end= 1                 # required for functions c
        #self.ncoeff= 4                   # number of coefficients
        #self.coeff=np.array([[]]).T      # required for function a

        #return



################################################################
#
# Transfer
#
################################################################
 

# Unpack u into coordinate and velocity sub-arrays
def u_to_Bodies(u):
    global Bodies
    global nB
        
    for Bi in range(1,nB):
        ir  = Bodies[Bi,0].irc
        ird = Bodies[Bi,0].irv
        
        Bodies[Bi,0].r  = np.atleast_2d( u[ir:ir +1 +1].flatten() ).T
        Bodies[Bi,0].p  = u[ir+2]
        Bodies[Bi,0].r_d = np.atleast_2d( u[ird:ird +1 +1].flatten() ).T    
        Bodies[Bi,0].p_d = u[ird+2] 
    return None
        
#%%% Bodies_to_u
def Bodies_to_u(u):
    global nB
    global nB6
    global Bodies
    
    u= np.zeros((nB6,1))
    for Bi in range(1,nB):
        ir  = Bodies[Bi,0].irc
        ird = Bodies[Bi,0].irv
        u[ir:ir+2+1]   = np.atleast_2d(np.concatenate((Bodies[Bi,0].r, Bodies[Bi,0].p),axis=None)).T
        u[ird:ird+2+1] = np.atleast_2d(np.concatenate((Bodies[Bi,0].r_d, Bodies[Bi,0].p_d),axis=None)).T
    return u
    
#%%% Bodies_to_u_d
# Transfer Bodies to u
def Bodies_to_u_d():
    global nB6
    global nB
    global Bodies
    
    u_d = np.zeros((nB6, 1))
    for Bi in range(1, nB):
        ir = Bodies[Bi,0].irc
        ird = Bodies[Bi,0].irv
        u_d[ir:ir + 2+1] = np.atleast_2d(np.concatenate((Bodies[Bi,0].r_d, Bodies[Bi,0].p_d), axis=None)).T
        u_d[ird:ird + 2+1] = np.atleast_2d(np.concatenate((Bodies[Bi,0].r_dd, Bodies[Bi,0].p_dd), axis=None)).T
    return u_d




################################################################
#
# ANIMATION PLOTTER
#
################################################################
 
def plot_system():                    # 2D Animation
##### include global variables 
    global Bodies, nB, nB3, nB6      
    global Points, nP, Points_anim, nPanim, nPtot
    global Uvectors, nU 
    global Joints, nJ, nConst
    global Forces, nF
    global M_array, M_inv_array
    global Functs, nFc
    global ZZ, redund, cfriction
    global num, D, Dt, Lambda 
    global xmin, xmax, ymin, ymax
    global showtime, t10
    global flags, pen_d0

##### set axis limits 
    #max_val = max(xmax, ymax)
    #min_val = min(xmin, ymin)
    #plt.xlim(xmin, xmax)
    #plt.ylim(ymin, ymax)
    plt.gca().set_aspect('equal')
    
##### Plot body centre points 
    for Bi in range(1,nB):
        plt.plot(Bodies[Bi,0].r[0,0],Bodies[Bi,0].r[1,0],'ko' )
        plt.text(Bodies[Bi,0].r[0,0],Bodies[Bi,0].r[1,0],'   (%i'%Bi)
        plt.text(Bodies[Bi,0].r[0,0],Bodies[Bi,0].r[1,0],'       )')
    #plt.show()
##### Draw lines between body centers and points on those bodies 
    print("NUmber of bodies " , nB)
    for Bi in range(1,nB):
        print("BODY INDEX",Bi)
        npts = len(Bodies[Bi,0].pts)
        linecolor = Bodies[Bi,0].color
        linecolor = "k"
        #for j in range(1-1,npts): 
        print("NUmber of points: " ,npts)
        print(Bodies[Bi, 0].pts)
        for j in range(npts):
            
        #for j in range(npts):
            a1 = Bodies[Bi,0].r[0,0]
            a2 = Points[int(Bodies[Bi,0].pts[j,0]),0].rP[0][0]
            b1 = Bodies[Bi,0].r[1,0]
            b2 = Points[int(Bodies[Bi,0].pts[j,0]),0].rP[1][0]
            plt.plot([a1, a2], [b1, b2], color = linecolor, linewidth=1)
            #print(Bi,j)
            #print(Bodies[Bi,0].pts)
            #print(Points[int(Bodies[Bi,0].pts[j,0]),0].rP)
            print("Point index",int(Bodies[Bi,0].pts[j,0]))
            print(Points[int(Bodies[Bi,0].pts[j,0]),0].rP[0][0])
            print(Points[int(Bodies[Bi,0].pts[j,0]),0].rP[1][0])
            #print(Bodies[Bi,0].pts)
            #print(Points
    #plt.show()
            
    #print("Number of points",nP)
##### Plot points that are defined by 's' vectors
    for i in range(1,nP):
        plt.plot(Points[i,0].rP[0][0], Points[i,0].rP[1][0],'ko', markerfacecolor='k', markersize=2)
        plt.plot(Points[i,0].rP[0][0], Points[i,0].rP[1][0],'ko', markerfacecolor='k', markersize=2) 
        print("POINTS")
        print(i)
        print(Points[i,0].rP[0][0])
        print(Points[i,0].rP[1][0])
        
    #plt.show()
##### Draw lines between points that are connected by springs 
    for i in range(1,nF):
        
        # define switch 
        class switch(object):
            def force_type(self, argument):                            # Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
                return method()                                        # Call the method as we return it
        
            # define "cases"      
            def ptp(self):
                pt1 = Forces[i,0].iPindex 
                pt2 = Forces[i,0].jPindex
                a1  = Points[int(pt1),0].rP[0][0]
                a2  = Points[int(pt2),0].rP[0][0]
                b1  = Points[int(pt1),0].rP[1][0]
                b2  = Points[int(pt2),0].rP[1][0]
                plt.plot([a1, a2], [b1, b2], color='m',linestyle='--')
                
        switch().force_type(Forces[i,0].type) # implement switch 
        
    for Ji in range(1,nJ):
        
        # define switch 
        class switch(object):
            def joint_type(self, argument):                            # Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
                return method()                                        # Call the method as we return it
        
            # define "cases" 
            def rev_rev(self): 
                Pi = Joints[Ji,0].iPindex
                Pj = Joints[Ji,0].jPindex
                a1 = Points[Pi,0].rP[0][0]
                a2 = Points[Pj,0].rP[0][0]
                b1 = Points[Pi,0].rP[1][0]
                b2 = Points[Pj,0].rP[1][0]
                plt.plot([a1, a2], [b1, b2], color='k')            
                
            def rev_tran(self): 
                Pi = Joints[Ji,0].iPindex
                plt.plot(Points[Pi,0].rP[0][0] , Points[Pi-1,0].rP[1][0],'ko', markerfacecolor='k',markersize=4)            
                
        # implement switch 
        switch().joint_type(Joints[Ji,0].type)                    

    for Bi in range(1,nB):
        
        linecolor = Bodies[Bi,0].color   
        
        # define switch 
        class switch(object):
            def body_shape(self, argument): #Dispatch method
                method_name = argument
                method = getattr(self, method_name, lambda: "Invalid") # Get the method from 'self'. Default to a lambda.
                return method()                                        # Call the method as we return it
            
            # define "cases" 
            def circle(self):
                radius = Bodies[Bi,0].R

                w1x = Bodies[Bi,0].r[0,0]
                w1y = Bodies[Bi,0].r[1,0]
                
                w1 = plt.Circle((w1x, w1y), radius, color='k', fill=False)
                plt.gca().add_patch(w1)
                
            def rect(self):
                P5 = np.zeros((2,5))

                for i in range(0,4):
                    P5[:,i] = Bodies[Bi,0].r.T + Bodies[Bi,0].A@Bodies[Bi,0].P4[:,i].T
                
                P5[:,5-1] = P5[:,1-1]
                for i in range(0,4):
                    plt.plot([P5[1-1,i], P5[1-1,i+1]], [P5[2-1,i], P5[2-1,i+1]], color='k')

            def line(self):
                P5 = np.zeros((2,2))
                for i in range(1-1,2):
                    P5[:,i] = Bodies[Bi,0].r.T + Bodies[Bi,0].A@Bodies[Bi,0].P4[:,i]
                
                plt.plot([P5[1-1,1-1], P5[1-1,2-1]], [P5[2-1,1-1], P5[2-1,2-1]],color='k')

        switch().body_shape(Bodies[Bi,0].shape) # implement switch 

    plt.grid()
    return None    



################################################################
#
# UPDATES
#
################################################################
 
#%%% Update_Position
def Update_Position():
    global Bodies
    global Points
    global nB 
    global nP 
    global nU 
    global Uvectors
    
    # Update_Position
    # Compute A's
    for Bi in range(1, nB):
        B_A_ = np.concatenate( (Matrix_A(Bodies[Bi,0].p)), axis=None)
        B_A_1 = np.array([ [ B_A_[0],B_A_[1] ] ])
        B_A_2 = np.array([ [ B_A_[2],B_A_[3] ] ])
        Bodies[Bi,0].A = np.concatenate( (B_A_1, B_A_2),axis=0)
    
    # Compute sP = A * sP_prime; rP = r + sP    
    for Pi in range(1, nP):
        Bi = Points[Pi,0].Bindex
        if Bi != 0:
            Points[Pi,0].sP = np.matmul(Bodies[Bi,0].A, Points[Pi,0].sPlocal)
            Points[Pi,0].sP_r = s_rot(Points[Pi,0].sP)
            Points[Pi,0].rP = Bodies[Bi,0].r + Points[Pi,0].sP
            
    for Vi in range(1, nU):
        Bi = Uvectors[Vi,0].Bindex
        if Bi != 0:
            Uvectors[Vi,0].u = np.matmul(Bodies[Bi,0].A, Uvectors[Vi,0].ulocal)
            Uvectors[Vi,0].u_r = s_rot(Uvectors[Vi,0].u)
                      
#%%% Update_Velocity
def Update_Velocity():
    # Update_Velocity
    # Compute sP_dot and rP_dot vectors
    global Points
    global Uvectors
    global Bodies
    global nP
    global nU
    
    for Pi in range(1, nP):
        Bi = Points[Pi,0].Bindex
        if Bi != 0:
            Points[Pi,0].sP_d = Points[Pi,0].sP_r * Bodies[Bi,0].p_d
            Points[Pi,0].rP_d = Bodies[Bi,0].r_d + Points[Pi,0].sP_d
    
    # Compute u_dot vectors
    for Vi in range(1, nU):
        Bi = Uvectors[Vi,0].Bindex
        if Bi != 0:
            Uvectors[Vi,0].u_d = Uvectors[Vi,0].u_r * Bodies[Bi,0].p_d



#######################################################################
#
# MAIN SOLVER
#
#######################################################################





#sys.argv 
#import 

#print(sys.argv)
folder = sys.argv[1]
exec(open(os.path.join(folder, 'dapInputSettings.py')).read())


#folder = "/tmp/"
exec(open(os.path.join(folder, 'inBodies.py')).read())
exec(open(os.path.join(folder, 'inForces.py')).read())
exec(open(os.path.join(folder, 'inFuncts.py')).read())
exec(open(os.path.join(folder, 'inJoints.py')).read())
exec(open(os.path.join(folder, 'inPoints.py')).read())
exec(open(os.path.join(folder, 'inUvectors.py')).read())



#print(Points[1::])
#broekn
Points_anim = np.array([[]]).T

initialize()


showtime = 1 #TODO do we really need this?

u = np.zeros( (6*(nB),1) )
u = Bodies_to_u(u)


Tspan  = np.arange(t_initial,t_final,dt)
Tarray = np.zeros( (len(Tspan), len(u)) )


Tarray[0,:] = np.concatenate((u), axis=None)

r = integrate.ode(analysis).set_integrator("dop853") # choice of method

r.set_initial_value(u,t_initial)                     # initial values


for i in range(1, Tspan.size):
    Tarray[i, :] = np.concatenate((r.integrate(Tspan[i])),axis=None)
Tarray_final = Tarray[:,1:(6*(nB-1)+1)]
if not r.successful():
    raise RuntimeError("Could not integrate")


outFile = os.path.join(folder, "dapResults.npy")
np.save(outFile, Tarray)

print("Done")

print(Tarray)

if animate:
    
    nt = len(Tspan)
    nP = nPtot

    pause_time = 0.01
    #Update_Position()
    
    #for Bi in range(1,nB):
        
        #if Bodies[Bi,0].shape == 'rect':    
            #w2 = Bodies[Bi,0].W/2
            #h2 = Bodies[Bi,0].H/2
            #Bodies[Bi,0].P4 = np.array([[w2, -w2, -w2,  w2,],
                                        #[h2,  h2, -h2, -h2]]) 
            
        #if Bodies[Bi,0].shape == 'line':
            #if Bodies[Bi,0].W == 0:
                #h2 = Bodies[Bi,0].R/2
                #Bodies[Bi,0].P4 = np.array([[0,  0],
                                            #[h2 ,-h2]])
            #else:
                #w2 = Bodies[Bi,0].R/2
                #Bodies[Bi,0].P4 = np.array([[w2, -w2],
                                            #[0,  0]])
    
    #plot_system()
    
    for i in range(1,nt):
        u = Tarray[i,:].T
        u_to_Bodies(u)
        Update_Position()
        plt.clf()
        plot_system() 
        plt.pause(pause_time)
        #if Tspan[i-1] == 0:
            #if nt>1:
                #input('Press Enter to continue...') 

    #plt.show()
else:
    print('Done solving')
