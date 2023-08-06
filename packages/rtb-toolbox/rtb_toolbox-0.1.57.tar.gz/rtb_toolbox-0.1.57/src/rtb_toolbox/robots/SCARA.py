import numpy as np
import sympy as sp

from rtb_toolbox.forward_kinematics import ForwardKinematic
from rtb_toolbox.link import Link


q1, q2, q4 = sp.symbols('q_1 q_2 q_4')
d3 = sp.symbols('d_3')

j0 = Link([q1,  0, .2,  0    ])
j1 = Link([q2,  0,.15,  sp.pi])
j2 = Link([0 , d3, 0,   0    ], offset=0.1, link_type='P')
j3 = Link([q4,0.8, 0,   0    ])


scara_fk = ForwardKinematic(
    [j0, j1, j2, j3],
)
