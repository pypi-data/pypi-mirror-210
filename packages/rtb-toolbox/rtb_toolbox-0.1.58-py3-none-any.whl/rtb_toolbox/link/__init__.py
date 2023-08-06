from rtb_toolbox.utils import compute_link_transformation, np

class Link:
    def __init__(
            self,
            dhp,
            offset                = 0,
            mass                  = 0,
            transformation_matrix = None,
            inertia_tensor        = np.eye(3),
            limits                = [-np.pi, np.pi],
            link_type             = 'R',
            v                     = None
    ):
        self.dhp = dhp
        self.inertia_tensor = inertia_tensor
        self.limits = limits
        self.link_type = link_type
        self.offset = offset
        self.v = v

        if dhp is None:
            raise ValueError('dhp must be specified')
        
        self.generalized_coordinate = dhp[0] if link_type == 'R' else dhp[1]

        self.mass = mass
        self.transformation_matrix = transformation_matrix

        if transformation_matrix is None:
            self.update()

    def update(self):
        tm = compute_link_transformation(self.dhp, self.offset, self.link_type)

        if self.v != None:
            tm = self.v@tm

        self.transformation_matrix = tm

    def get_transformation_matrix(self):
        return self.transformation_matrix
