import numpy as np
import sympy as sp

from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.termination.default import MaximumGenerationTermination

from rtb_toolbox.forward_kinematics import ForwardKinematic
from rtb_toolbox.frame import xyz_rotation_matrix, translation_matrix
from rtb_toolbox.utils import matrix_log6, inverse_transformation, se3_to_vec, normalize_angle_between_limits


class InverseKinematicProblem(Problem):
    def __init__(
            self,
            desired_pose=None,
            fk: ForwardKinematic = None,
    ):
        lb = [fk.links[i].limits[0] for i in range(fk.len_links)]
        ub = [fk.links[i].limits[1] for i in range(fk.len_links)]

        super().__init__(n_var=fk.len_links, n_obj=1, n_constr=0, xl=lb, xu=ub)

        self.desired_pose = desired_pose
        self.fk = fk
    
    def _evaluate(self, X, out, *args, **kwargs):
        iters = X.shape[0]
        F = np.zeros((iters, 1))

        fk = self.fk
        desired_pose = self.desired_pose

        for i in range(iters):
            Q = X[i, :]

            htm = fk.compute_ee_transformation_matrix(Q)
            i_htm = inverse_transformation(htm)

            T_bd = i_htm @ desired_pose
            log_tbd = matrix_log6(T_bd)

            s = se3_to_vec(log_tbd)
            n_s = np.linalg.norm(s)

            F[i] = n_s
        
        out["F"] = F


def evolutive_ik(
        desired_transformation=None,
        fk: ForwardKinematic = None,
        initial_guess=None,
        max_iterations=2048,
        verbose=False,
        algorithm=None,
):
    if initial_guess is None:
        initial_guess = np.random.rand(fk.len_links)

    desired_rotation = xyz_rotation_matrix(desired_transformation[3], desired_transformation[4],
                                             desired_transformation[5])

    desired_pose = sp.matrix2numpy(translation_matrix(desired_transformation[0], desired_transformation[1],
                                                      desired_transformation[2]) @ desired_rotation, dtype=np.float64)

    termination = MaximumGenerationTermination(
        n_max_gen=max_iterations
    )

    problem = InverseKinematicProblem(
        desired_pose=desired_pose,
        fk=fk,
    )

    if algorithm is None:
        from pymoo.algorithms.soo.nonconvex.cmaes import CMAES

        algorithm = CMAES(
            restarts=2,
            bipop=True,
            sigma=1,
            tolfun=1e-8,
            tolx=1e-8,
        )

    res = minimize(
        problem,
        algorithm,
        termination,
        verbose=verbose,
        save_history=False,
    )

    f = res.F.min()
    theta_i = res.X
    success = f < 1e-5

    return theta_i, desired_pose, success, f


def position_ik(
        desired_position=None,
        fk: ForwardKinematic = None,
        initial_guess=None,
        f_tolerance=1e-7,
        max_iterations=1500,
        lmbd=.1,
        verbose=False,
        normalize=False
):
    desired_position = np.array([
        [desired_position[0]],
        [desired_position[1]],
        [desired_position[2]]
    ])

    if initial_guess is None:
        initial_guess = np.random.rand(6)

    theta_i = initial_guess.copy()

    F = f_tolerance + 1
    i = 0

    while F > f_tolerance and i < max_iterations:
        P_i = fk.compute_ee_position(theta_i)
        G = P_i - desired_position

        F = .5 * G.T @ G

        J_k = fk.compute_jacobian(theta_i)[3:, :]

        theta_i -= lmbd * (np.linalg.pinv(J_k) @ G)[:, 0]

        i += 1

        if verbose:
            print(f'Iteration {i}, F = {F}')

    error = F > f_tolerance

    if normalize:
        for i in range(fk.len_links):
            link_limits = fk.links[i].limits

            theta = normalize_angle_between_limits(
                theta_i[i],
                link_limits[0],
                link_limits[1]
            )

            theta_i[i] = theta

    return theta_i, desired_position, not error


def full_ik(
        desired_transformation=None,
        fk: ForwardKinematic = None,
        initial_guess=None,
        epsilon_wb=1e-5,
        epsilon_vb=1e-5,
        max_iterations=1000,
        lmbd=.1,
        verbose=False,
        only_position=False,
        normalize=True):

    if only_position:
        return position_ik(
            desired_position=desired_transformation[:3],
            fk=fk,
            initial_guess=initial_guess,
            f_tolerance=epsilon_vb,
            max_iterations=max_iterations,
            lmbd=lmbd,
            verbose=not verbose)

    # transformation_data = [x, y, z, rx, ry, rz]
    # x, y, z: position of the end effector
    # rx, ry, rz: orientation of the end effector
    # returns: the joint angles

    if initial_guess is None:
        initial_guess = initial_guess = np.random.rand(6)

    desired_rotation = xyz_rotation_matrix(desired_transformation[3], desired_transformation[4],
                                             desired_transformation[5])

    desired_pose = sp.matrix2numpy(translation_matrix(desired_transformation[0], desired_transformation[1],
                                                      desired_transformation[2]) @ desired_rotation, dtype=np.float64)

    theta_i = initial_guess.copy()

    error = True
    i = 0

    while error and i < max_iterations:
        htm = fk.compute_ee_transformation_matrix(theta_i)
        i_htm = inverse_transformation(htm)

        T_bd = i_htm @ desired_pose
        log_tbd = matrix_log6(T_bd)

        s = se3_to_vec(log_tbd)

        J = fk.compute_jacobian(theta_i)

        d_theta = np.linalg.pinv(J) @ s
        theta_i += (lmbd * d_theta)

        wb_err = np.linalg.norm(s[:3])
        vb_err = np.linalg.norm(s[3:])

        error = wb_err > epsilon_wb or vb_err > epsilon_vb

        i += 1

        if verbose:
            print(f'Iteration {i}, s = {s}')

    return theta_i, desired_pose, np.linalg.norm(s)
