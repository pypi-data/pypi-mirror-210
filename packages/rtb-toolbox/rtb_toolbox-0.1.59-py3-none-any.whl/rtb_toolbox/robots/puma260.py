import numpy as np
import sympy as sp

from rtb_toolbox.forward_kinematics import ForwardKinematic
from rtb_toolbox.link import Link

q1, q2, q3, q4, q5, q6 = sp.symbols('q_1 q_2 q_3 q_4 q_5 q_6')

j0 = Link([q1, 13, 0,  sp.pi / 2])
j1 = Link([q2,  3, 8,         0 ])
j2 = Link([q3,  0, 0,  sp.pi / 2], offset=sp.pi / 2)
j3 = Link([q4,  8, 0, -sp.pi / 2])
j4 = Link([q5,  0, 0, -sp.pi / 2], offset=-sp.pi / 2)
j5 = Link([q6,  4, 0,          0])


puma260_fk = ForwardKinematic(
    [j0, j1, j2, j3, j4, j5],
)
