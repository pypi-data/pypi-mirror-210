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
"""Module for NodeRegistry."""
import inspect
from functools import partial

import qctrlcommons.node.composite.filter_and_resample
import qctrlcommons.node.composite.optimizable_signals
import qctrlcommons.node.composite.signals
import qctrlcommons.node.composite.signals_pwc
import qctrlcommons.node.composite.signals_stf
from qctrlcommons.node.composite.namespace import COMPOSITE_ATTR


def _register(modules):
    """
    Collect exposed composite nodes from modules.
    """
    registered = []
    for module in modules:
        for _, member in inspect.getmembers(
            module, predicate=partial(_filter, module_name=module.__name__)
        ):
            registered.append(member)
    return registered


def _filter(member, module_name):
    """
    - Exposed member must be a function.
    - Exposed member must be defined in the module, not imported.
    - Exposed member must not be private.
    """
    return (
        (inspect.isfunction(member) or inspect.isclass(member))
        and member.__module__ == module_name
        and not member.__name__.startswith("_")
        and hasattr(member, COMPOSITE_ATTR)
    )


COMPOSITE_NODE_REGISTRY = _register(
    [
        qctrlcommons.node.composite.optimizable_signals,
        qctrlcommons.node.composite.filter_and_resample,
        qctrlcommons.node.composite.signals_pwc,
        qctrlcommons.node.composite.signals_stf,
        qctrlcommons.node.composite.signals,
    ]
)
