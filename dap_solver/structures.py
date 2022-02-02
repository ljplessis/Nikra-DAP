import numpy as np 
#%%% Body Structure
class Body_struct:
    def __init__(self):
        
        self.m      = 1                      # mass
        self.J      = 1                      # moment of inertia
        self.r      = np.array([[0,0]]).T 	 # x, y coordinates
        self.p      = 0                      # angle phi
        self.r_d    = np.array([[0,0]]).T    # time derivative of x and y
        self.p_d    = 0                      # time derivative of phi
        self.A      = np.eye(2)              # rotational transformation matrix
        self.r_dd   = np.array([[0,0]]).T    # x_double_dot,y_double_dot
        self.p_dd   = 0                      # 2nd time derivative of phi  #  index of the 1st element of r in u or u_dot
        self.irc    = 0                      # index of 1st element of r in u or u_dot
        self.irv    = 0                      # index of the 1st element of r_dot in u or u_dot
        self.ira    = 0                      # index of the 1st element of r_dot2 in v_dot

        self.m_inv  = 1                         # mass inverse
        self.J_inv  = 1                         # inverse of moment of inertia
        self.wgt    = np.array([[0,0]]).T       # weight of body as a force vector
        self.f      = np.array([[0,0]]).T       # sum of forces that act on the body
        self.n      = 0                         # sum of moments that act on the body
        self.shape  = ''                        # 'circle', 'rect', line
        self.R      = 1                         # radius of the circle
        self.circ   = np.array([[]]).T          # points on circumference of the circle
        self.W      = 0                         # width of the rectangle
        self.H      = 0                         # height of the rectangle
        self.color  ='k'                        # default color for the body
        self.P4     = np.array([[]]).T          # corners of the rectangle
        self.pts    = np.array([[]]).T          # point indexes associated with this body
        return
    def __str__(self):
        return str(self.__dict__)

#%% Force Structure
class Force_struct:
    def __init__(self):
        self.type       = 'ptp'                 # element type: ptp, rot_sda, weight, fp, f, T
        self.iPindex    = 0                     # index of the head (arrow) point
        self.jPindex    = 0                     # index of the tail point
        self.iBindex    = 0                     # index of the head (arrow) body
        self.jBindex    = 0                     # index of the tail body
        self.k          = 0                     # spring stiffness
        self.L0         = 0                     # undeformed length
        self.theta0     = 0                     # undeformed angle
        self.dc         = 0                     # damping coefficient
        self.f_a        = 0                     # constant actuator force
        self.T_a        = 0                     # constant actuator torque
        self.gravity    = 9.81                  # gravitational constant
        self.wgt        = np.array([[0,-1]]).T  # gravitational direction
        self.flocal     = np.array([[0,0]]).T   # constant force in local frame
        self.f          = np.array([[0,0]]).T   # constant force in x-y frame
        self.t          = 0                     # constant torque in x-y frame
        self.iFunct     = 0
        return
    
    def __str__(self):
        return str(self.__dict__)


#%%% Joint Structure
class Joint_struct:
    def __init__(self):
        self.type       = 'rev'     # joint type: rev, tran, rev-rev, rev-tran, rigid, disc, rel-rot, rel-tran

        self.iBindex    = 0         # body index i
        self.jBindex    = 0         # body index j
        self.iPindex    = 0         # point Pi index
        self.jPindex    = 0         # point Pj index
        self.iUindex    = 0         # unit vector u_i index
        self.jUindex    = 0         # unit vector u_j index
        self.iFunct     = 0         # analytical function index
        self.L          = 0         # constant length

        self.R      = 1                 # constant radius
        self.x0     = 0                 # initial condition x for disc
        self.p0     = 0                 # initial condition phi for a disc (or rigid)
        self.d0     = np.array([[]]).T  # initial condition for d (rigid)
        self.fix    = 0                 # fix relative dof if = 1 (rev or tran)
        self.nbody  = 2                 # number of moving bodies involved
        self.mrows  = 2                 # number of rows (constraints)

        self.rows     = 0               # row index-start
        self.rowe     = 0               # row index-end
        self.colis    = 0               # column index for body i-start
        self.colie    = 0               # column index for body i-end
        self.coljs    = 0               # column index for body j-start
        self.colje    = 0               # column index for body j-end
        self.lagrange =np.zeros((3,1))  # Lagrange multipliers
        return
    
    def __str__(self):
        return str(self.__dict__)


#%%% Point Structure
class Point_struct:
    def __init__(self):
        self.Bindex     = 0                     # body index
        self.sPlocal    = np.array([[0,0]]).T   # body-fixed coordinates
        self.sP         = np.array([[0,0]]).T   # x, y components of vector s
        self.sP_r       = np.array([[0,0]]).T   # vector s rotated
        self.rP         = np.array([[0,0]]).T   # x, y coordinates of the point
        self.sP_d       = np.array([[0,0]]).T   # s_P_dot
        self.rP_d       = np.array([[0,0]]).T   # r_P_dot
        self.rP_dd      = np.array([[0,0]]).T   # r_P_dot2
        return
    
    def __str__(self):
        return str(self.__dict__)


#%%% Unit Structure
class Unit_struct:
    def __init__(self):
        self.Bindex = 0                     # body index
        self.ulocal = np.array([[1,0]]).T   # u_prime; xi and eta components
        self.u      = np.array([[0,0]]).T   # x, y components
        self.u_r    = np.array([[0,0]]).T   # vector u rotated
        self.u_d    = np.array([[0,0]]).T   # u_dot
        return
    
    def __str__(self):
        return str(self.__dict__)

#%%% Function Structure
class Funct_struct:
    def __init__(self):
        self.type='a'                    # function type a, b, or c
        self.t_start=0                   # required for functions b, c
        self.f_start=0                   # required for functions b, c
        self.t_end=1                     # required for functions b, c
        self.f_end=1                     # required for functions b
        self.dfdt_end= 1                 # required for functions c
        self.ncoeff= 4                   # number of coefficients
        self.coeff=np.array([[]]).T      # required for function a
        return
    def __str__(self):
        return str(self.__dict__)
