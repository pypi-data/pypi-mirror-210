import numpy as np
import sympy as sp

from rtb_toolbox.forward_kinematics import ForwardKinematic
from rtb_toolbox.link import Link
from rtb_toolbox.frame import transformation_matrix

from sympy import pi

q1, q2, q3, q4, q5, q6 = sp.symbols('q_1 q_2 q_3 q_4 q_5 q_6')

v1 = transformation_matrix(0, 0, 260, pi, 0, 0)
v2 = transformation_matrix(0, 0, 0, 0, pi, 0)

joint_limits = np.deg2rad(
    np.array([
        [-170, 170],
        [-85, 155],
        [-170, 0],
        [-210, 210],
        [-130, 130],
        [-400, 400]
    ])
)

j0 = Link([q1,  0,     150,        pi/2], v=v1,           limits=joint_limits[0])
j1 = Link([q2,  0,     590,          pi], offset=-pi/2,   limits=joint_limits[1])
j2 = Link([q3,  0,     130,       -pi/2], offset=pi/2 ,   limits=joint_limits[2])
j3 = Link([q4, -647.07,  0,       -pi/2],                 limits=joint_limits[3])
j4 = Link([q5,  0,       0,        pi/2],                 limits=joint_limits[4])
j5 = Link([q6,-95,       0,           0], v=v2,           limits=joint_limits[5])

comau_fk = ForwardKinematic(
    [j0, j1, j2, j3, j4, j5],
)