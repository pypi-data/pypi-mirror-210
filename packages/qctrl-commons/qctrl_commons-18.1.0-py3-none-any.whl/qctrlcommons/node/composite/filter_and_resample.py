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
System-agnostic convenient nodes.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from qctrlcommons.node.composite.namespace import composite_node
from qctrlcommons.node.node_data import Pwc
from qctrlcommons.preconditions import check_argument


@composite_node
def filter_and_resample_pwc(
    graph: "Graph",
    pwc: Pwc,
    cutoff_frequency: float,
    segment_count: int,
    duration: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Filter a piecewise-constant function with a sinc filter and resample it again.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    pwc : Pwc
        The piecewise-constant function :math:`\alpha(t)` to be filtered.
    cutoff_frequency : float
        Upper limit :math:`\omega_c` of the range of angular frequencies that you want to
        preserve in your function.
    segment_count : int
        The number of segments of the resampled filtered function.
    duration : float, optional
        Force the resulting piecewise-constant function to have a certain duration.
        This option is mainly to avoid floating point errors when the total duration is
        too small. If not provided, it is set to the sum of segment durations of `pwc`.
        Defaults to None.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The filtered and resampled piecewise-constant function.

    See Also
    --------
    :func:`~qctrl.graphs.Graph.convolve_pwc` :
        Create the convolution of a piecewise-constant function with a kernel.
    :func:`~qctrl.graphs.Graph.discretize_stf` :
        Create a piecewise-constant function by discretizing a sampleable function.
    :func:`~qctrl.graphs.Graph.sinc_convolution_kernel` :
        Create a convolution kernel representing the sinc function.

    Notes
    -----
    The resulting filtered function is

    .. math::
        \int_{-\infty}^\infty \alpha(\tau)
        \frac{\sin[\omega_c (t-\tau)]}{\pi (t-\tau)} \mathrm{d}\tau
        = \frac{1}{2\pi} \int_{-\omega_c}^{\omega_c}
        e^{i \omega t} \hat\alpha(\omega) \mathrm{d}\omega

    where

    .. math::
        \hat\alpha(\omega)
        =\int_{-\infty}^\infty e^{-i \omega \tau}\alpha(\tau) \mathrm{d}\tau

    is the Fourier transform of :math:`\alpha(t)`. Hence the filter eliminates components of
    the signal that have angular frequencies greater than :math:`\omega_c`.
    """
    if duration is not None:
        check_argument(
            duration > 0,
            "The duration must be positive.",
            {"duration": duration},
        )

    total_duration = duration or np.sum(pwc.durations)

    return graph.discretize_stf(
        stf=graph.convolve_pwc(
            pwc=pwc, kernel=graph.sinc_convolution_kernel(cutoff_frequency)
        ),
        duration=total_duration,
        segment_count=segment_count,
        name=name,
    )
