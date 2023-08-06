# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Module for nodes related to open quantum systems.
"""
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

import forge
import numpy as np
from scipy.sparse import spmatrix

from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)
from qctrlcommons.node.utils import (
    TensorLike,
    check_argument,
    check_density_matrix_shape,
    check_lindblad_terms,
    check_oqs_hamiltonian,
)
from qctrlcommons.preconditions import (
    check_argument_hermitian,
    check_numeric_numpy_array,
    check_operator,
    check_sample_times_with_bounds,
)


class DensityMatrixEvolutionPwc(Node):
    r"""
    Calculate the state evolution of an open system described by the GKS–Lindblad master
    equation.

    The controls that you provide to this function have to be in piecewise-constant
    format. If your controls are smooth sampleable tensor-valued functions (STFs), you
    have to discretize them with `discretize_stf` before passing them to this function.
    You may need to increase the number of segments that you choose for the
    discretization depending on the sizes of oscillations in the smooth controls.

    By default, this function computes an approximate piecewise-constant solution for
    the consideration of efficiency, with the accuracy controlled by the
    parameter `error_tolerance`. If your system is small, you can set the
    `error_tolerance` to None to obtain an exact solution.

    Note that when using the exact method, both `hamiltonian` and `lindblad_terms`
    are converted to the dense representation, regardless of their original formats.
    This means that the computation can be slow and memory intensive when applied to large systems.

    When using the approximate method, the sparse representation is used internally if
    `hamiltonian` is a `SparsePwc`, otherwise the dense representation is used.

    Parameters
    ----------
    initial_density_matrix : np.ndarray or Tensor
        A 2D array of the shape ``(D, D)`` representing the initial density matrix of
        the system, :math:`\rho_{\rm s}`. You can also pass a batch of density matrices
        and the input data shape must be ``(B, D, D)`` where ``B`` is the batch dimension.
    hamiltonian : Pwc or SparsePwc
        A piecewise-constant function representing the effective system Hamiltonian,
        :math:`H_{\rm s}(t)`, for the entire evolution duration.
    lindblad_terms : list[tuple[float, np.ndarray or Tensor or scipy.sparse.spmatrix]]
        A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
        :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
        channel :math:`j`. You must provide at least one Lindblad term.
    sample_times : list or tuple or np.ndarray, optional
        A 1D array of length :math:`T` specifying the times :math:`\{t_i\}` at which this
        function calculates system states. Must be ordered and contain at least one element.
        Note that increasing the density of sample times does not affect the computation precision
        of this function. If omitted only the evolved density matrix at the final time of the
        system Hamiltonian is returned.
    error_tolerance : float, optional
        Defaults to 1e-6. This option enables an approximate method to solve the master
        equation, meaning the 2-norm of the difference between the propagated state and the exact
        solution at the final time (and at each sample time if passed) is within the error
        tolerance. Note that, if set, this value must be smaller than 1e-2 (inclusive).
        However, setting it to a too small value (for example below 1e-12) might result in slower
        computation, but would not further improve the precision, since the dominating error in
        that case is due to floating point error. You can also explicitly set this option to
        None to find the exact piecewise-constant solution. Note that using the exact solution
        can be very computationally demanding in calculations involving a large Hilbert space or
        a large number of segments.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(complex)
        System states at sample times. The shape of the return value is ``(D, D)`` or
        ``(T, D, D)``, depending on whether you provide sample times.
        Otherwise, the shape is ``(B, T, D, D)`` if you provide a batch of initial states.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    sparse_pwc_operator : Create `SparsePwc` operators.
    state_evolution_pwc : Corresponding operation for coherent evolution.
    steady_state : Compute steady state of open quantum system.

    Notes
    -----
    Under the Markovian approximation, the dynamics of an open quantum system can be described by
    the GKS–Lindblad master equation [1]_ [2]_

    .. math::
        \frac{{\rm d}\rho_{\rm s}(t)}{{\rm d}t} = -i [H_{\rm s}(t), \rho_{\rm s}(t)]
        + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\rm s}(t) ,

    where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
    system evolution and defined as

    .. math::
        {\mathcal D}[X]\rho := X \rho X^\dagger
            - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

    for any system operator :math:`X`.

    This function uses sparse matrix multiplication when the Hamiltonian is passed as a
    `SparsePwc` and the Lindblad operators as sparse matrices. This leads to more efficient
    calculations when they involve large operators that are relatively sparse (contain mostly
    zeros). In this case, the initial density matrix is still a densely represented array or tensor.

    References
    ----------
    .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
            J. Math. Phys. 17, 821 (1976).
            <https://doi.org/10.1063/1.522979>`_
    .. [2] `G. Lindblad,
            Commun. Math. Phys. 48, 119 (1976).
            <https://doi.org/10.1007/BF01608499>`_

    Examples
    --------
    Simulate a trivial decay process for a single qubit described by the following master equation
    :math:`\dot{\rho} = -i[\sigma_z / 2, \, \rho] + \mathcal{D}[\sigma_-]\rho`.

    >>> duration = 20
    >>> initial_density_matrix = np.array([[0, 0], [0, 1]])
    >>> hamiltonian = graph.constant_pwc_operator(
    ...     duration=duration, operator=graph.pauli_matrix("Z") / 2
    ... )
    >>> lindblad_terms = [(1, graph.pauli_matrix("M"))]
    >>> graph.density_matrix_evolution_pwc(
    ...     initial_density_matrix, hamiltonian, lindblad_terms, name="decay"
    ... )
    <Tensor: name="decay", operation_name="density_matrix_evolution_pwc", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["decay"])
    >>> result.output["decay"]["value"]
    array([[9.99999998e-01+0.j, 0.00000000e+00+0.j],
           [0.00000000e+00+0.j, 2.06115362e-09+0.j]])

    See more examples in the `How to simulate open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-open-system-dynamics>`_
    and `How to simulate large open system dynamics
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
    user guides.
    """

    name = "density_matrix_evolution_pwc"
    args = [
        forge.arg("initial_density_matrix", type=TensorLike),
        forge.arg("hamiltonian", type=Union[Pwc, SparsePwc]),
        forge.arg(
            "lindblad_terms",
            type=List[Tuple[float, Union[np.ndarray, Tensor, spmatrix]]],
        ),
        forge.arg(
            "sample_times", type=Optional[Union[list, tuple, np.ndarray]], default=None
        ),
        forge.arg("error_tolerance", type=Optional[float], default=1e-6),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        sample_times = kwargs.get("sample_times")
        initial_density_matrix = kwargs.get("initial_density_matrix")
        hamiltonian = kwargs.get("hamiltonian")
        lindblad_terms = kwargs.get("lindblad_terms")
        error_tolerance = kwargs.get("error_tolerance")

        check_argument(
            isinstance(hamiltonian, (Pwc, SparsePwc)),
            "Hamiltonian must be a Pwc or a SparsePwc.",
            {"hamiltonian": hamiltonian},
        )
        if isinstance(hamiltonian, Pwc):
            check_argument(
                hamiltonian.batch_shape == (),
                "Hamiltonian cannot contain a batch.",
                {"hamiltonian": hamiltonian},
                extras={"hamiltonian.batch_shape": hamiltonian.batch_shape},
            )
        check_operator(initial_density_matrix, "initial_density_matrix")
        check_argument(
            not isinstance(initial_density_matrix, spmatrix),
            "Initial density matrix must not be sparse.",
            {"initial_density_matrix": initial_density_matrix},
        )

        if error_tolerance is not None:
            check_argument(
                error_tolerance <= 1e-2,
                "`error_tolerance` must not be greater than 1e-2.",
                {"error_tolerance": error_tolerance},
            )
        if sample_times is not None:
            sample_times = np.asarray(sample_times)
            check_sample_times_with_bounds(
                sample_times, "sample_times", hamiltonian, "hamiltonian"
            )
        check_density_matrix_shape(initial_density_matrix, "initial_density_matrix")
        check_oqs_hamiltonian(hamiltonian, initial_density_matrix)
        check_lindblad_terms(
            lindblad_terms, initial_density_matrix, "initial_density_matrix"
        )

        initial_state_shape = initial_density_matrix.shape
        if sample_times is None:
            shape = initial_state_shape
        else:
            shape = (
                initial_state_shape[:-2]
                + (len(sample_times),)
                + initial_state_shape[-2:]
            )
        return Tensor(_operation, shape=shape)


class SteadyState(Node):
    r"""
    Find the steady state of a time-independent open quantum system.

    The Hamiltonian and Lindblad operators that you provide have to give
    rise to a unique steady state.

    Parameters
    ----------
    hamiltonian : Tensor or spmatrix
        A 2D array of shape ``(D, D)`` representing the time-independent
        Hamiltonian of the system, :math:`H_{\rm s}`.
    lindblad_terms : list[tuple[float, np.ndarray or Tensor or scipy.sparse.spmatrix]]
        A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
        :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
        channel :math:`j`. You must provide at least one Lindblad term.
    method : str, optional
        The method used to find the steady state.
        Must be one of "QR", "EIGEN_SPARSE", or "EIGEN_DENSE".
        The "QR" method obtains the steady state through a QR decomposition and is suitable
        for small quantum systems with dense representation.
        The "EIGEN_SPARSE" and "EIGEN_DENSE"  methods find the steady state as the eigenvector
        whose eigenvalue is closest to zero, using either a sparse or a dense representation
        of the generator.
        Defaults to "QR".
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The density matrix representing the steady state of the system.

    Warnings
    --------
    This function currently does not support calculating the gradient with respect to its inputs.
    Therefore, it cannot be used in a graph for a `calculate_optimization` or
    `calculate_stochastic_optimization` call, which will raise a `RuntimeError`.
    Please use gradient-free optimization if you want to perform an optimization task with this
    function. You can learn more about it in the
    `How to optimize controls using gradient-free optimization
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-using-gradient-free-optimization>`_
    user guide.

    See Also
    --------
    density_matrix_evolution_pwc : State evolution of an open quantum system.

    Notes
    -----
    Under the Markovian approximation, the dynamics of an open quantum system can be described by
    the GKS–Lindblad master equation [1]_ [2]_,

    .. math::
        \frac{{\rm d}\rho_{\rm s}(t)}{{\rm d}t} = {\mathcal L} (\rho_{\rm s}(t)) ,

    where the Lindblad superoperator :math:`{\mathcal L}` is defined as

    .. math::
        {\mathcal L} (\rho_{\rm s}(t)) = -i [H_{\rm s}(t), \rho_{\rm s}(t)]
        + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\rm s}(t) ,

    where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
    system evolution and defined as

    .. math::
        {\mathcal D}[X]\rho := X \rho X^\dagger
            - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

    for any system operator :math:`X`.

    This function computes the steady state of :math:`{\mathcal L}` by solving

    .. math:: \frac{{\rm d}\rho_{\rm s}(t)}{{\rm d}t} = 0 .

    The function assumes that :math:`H_{\rm s}` is time independent
    and that the dynamics generated by :math:`{\mathcal L}`
    give rise to a unique steady state. That is, the generated quantum dynamical map
    has to be ergodic [3]_.

    References
    ----------
    .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
            J. Math. Phys. 17, 821 (1976).
            <https://doi.org/10.1063/1.522979>`_
    .. [2] `G. Lindblad,
            Commun. Math. Phys. 48, 119 (1976).
            <https://doi.org/10.1007/BF01608499>`_
    .. [3] `D. Burgarth, G. Chiribella, V. Giovannetti, P. Perinotti, and K. Yuasa,
            New J. Phys. 15 073045 (2013).
            <https://doi.org/10.1088/1367-2630/15/7/073045>`_

    Examples
    --------
    Compute the steady state of the single qubit open system dynamics according to the
    Hamiltonian :math:`H=\omega\sigma_z` and the single Lindblad operator :math:`L=\sigma_-`.

    >>> omega = 0.8
    >>> gamma = 0.5
    >>> hamiltonian = omega * graph.pauli_matrix("Z")
    >>> lindblad_terms = [(gamma, graph.pauli_matrix("M"))]
    >>> graph.steady_state(hamiltonian, lindblad_terms, name="steady_state")
    <Tensor: name="steady_state", operation_name="steady_state", shape=(2, 2)>
    >>> result = qctrl.functions.calculate_graph(graph=graph, output_node_names=["steady_state"])
    >>> result.output["steady_state"]["value"]
    array([[1.+0.j 0.-0.j]
           [0.-0.j 0.-0.j]])
    """

    name = "steady_state"
    args = [
        forge.arg("hamiltonian", type=Union[Tensor, spmatrix, np.ndarray]),
        forge.arg(
            "lindblad_terms",
            type=List[Tuple[float, Union[Tensor, spmatrix, np.ndarray]]],
        ),
        forge.arg("method", type=str, default="QR"),
    ]
    rtype = Tensor
    categories = [Category.LARGE_SYSTEMS, Category.TIME_EVOLUTION]
    supports_gradient = False

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian = kwargs.get("hamiltonian")
        lindblad_terms = kwargs.get("lindblad_terms")
        method = kwargs.get("method")

        check_argument(
            isinstance(hamiltonian, (Tensor, spmatrix, np.ndarray)),
            "Hamiltonian must be a Tensor, spmatrix or NumPy array.",
            {"hamiltonian": hamiltonian},
        )
        if isinstance(hamiltonian, spmatrix):
            check_argument_hermitian(hamiltonian, "hamiltonian")
        elif isinstance(hamiltonian, Tensor):
            check_operator(hamiltonian, "hamiltonian")
        elif isinstance(hamiltonian, np.ndarray):
            check_numeric_numpy_array(hamiltonian, "hamiltonian")
            check_argument_hermitian(hamiltonian, "hamiltonian")

        check_lindblad_terms(
            lindblad_terms=lindblad_terms,
            hilbert_space_object=hamiltonian,
            hilbert_space_object_name="hamiltonian",
        )

        if method is not None:
            check_argument(
                isinstance(method, str),
                "The method must be a string.",
                {"method": method},
            )
            check_argument(
                method in ["QR", "EIGEN_DENSE", "EIGEN_SPARSE"],
                'The method must be "QR", "EIGEN_DENSE", or "EIGEN_SPARSE".',
                {"method": method},
            )

        return Tensor(_operation, shape=hamiltonian.shape)
