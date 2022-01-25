import numpy as np
def Matrix_A(p): # This function computes the rotational transformation matrix A
    c = np.cos(p)
    s = np.sin(p)
    A = np.array([ [c, -s],
                   [s, c] ])
    return A


def s_rot(s): # This function rotates an array 90degrees positively 
    s_r = np.array([ [-s[1,0]], [s[0,0]] ])
    return s_r 
